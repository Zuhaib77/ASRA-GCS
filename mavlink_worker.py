import threading
import time
import math
import logging
from queue import Queue, Empty
from pymavlink import mavutil

# Import optimized configuration
try:
    from config import config, HEARTBEAT_TIMEOUT, CONNECTION_TIMEOUT
    from performance_monitor import PerformanceMonitor
    from logging_config import get_logger, log_mavlink
except ImportError:
    # Fallback for standalone use
    config = None
    HEARTBEAT_TIMEOUT = 3.0
    CONNECTION_TIMEOUT = 10.0
    PerformanceMonitor = None
    get_logger = logging.getLogger
    log_mavlink = lambda x: None

# Configuration constants with fallbacks
HEARTBEAT_CHECK_INTERVAL_SEC = 1.0
WORKER_LOOP_SLEEP_SEC = 0.01
DATA_RATE_CALCULATION_INTERVAL_SEC = 5.0
DATA_RATE_LOW_THRESHOLD_HZ = 1.0
COMMAND_ACK_TIMEOUT_SEC = 3

class MavlinkWorker(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self._conn = None
        self._running = False
        self._device = None
        self._baud = config.get("mavlink", "default_baud", 57600) if config else 57600
        self._out_queue = Queue()
        self._control_queue = Queue()
        self._last_heartbeat = 0
        self._connected = False
        self._is_armed = False
        self._lock = threading.Lock()
        
        # Logging
        self.logger = get_logger("mavlink_worker")
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor(config) if PerformanceMonitor else None
        
        # Connection recovery settings
        self.auto_reconnect = config.get("mavlink", "auto_reconnect", True) if config else True
        self.max_reconnect_attempts = config.get("mavlink", "max_reconnect_attempts", 3) if config else 3
        self.reconnect_delay = config.get("mavlink", "reconnect_delay", 2.0) if config else 2.0
        self.reconnect_attempts = 0
        
        # Message validation
        self.message_validation = config.get("mavlink", "message_validation", True) if config else True
        
        # Data quality tracking
        self._message_counts = {}
        self._last_message_time = {}
        self._data_rates = {}
        self._total_messages = 0

    def configure(self, device, baud):
        self._device = device
        self._baud = baud

    def connect(self):
        self._control_queue.put(("connect", None))

    def disconnect(self):
        self._control_queue.put(("disconnect", None))

    def arm_disarm(self):
        self._control_queue.put(("arm_disarm", None))

    def force_arm(self):
        self._control_queue.put(("force_arm", None))

    def set_mode(self, mode_id):
        self._control_queue.put(("set_mode", mode_id))

    def mission_start(self):
        self._control_queue.put(("mission_start", None))

    def abort_land(self):
        self._control_queue.put(("abort_land", None))

    def is_connected(self):
        with self._lock:
            return self._connected

    def is_armed(self):
        with self._lock:
            return self._is_armed

    def get_updates(self):
        updates = []
        while True:
            try:
                updates.append(self._out_queue.get_nowait())
            except Empty:
                break
        return updates

    def run(self):
        self._running = True
        last_heartbeat_check = time.time()
        
        while self._running:
            try:
                cmd, data = self._control_queue.get_nowait()
                if cmd == "connect": self._do_connect()
                elif cmd == "disconnect": self._do_disconnect()
                elif cmd == "arm_disarm": self._do_arm_disarm()
                elif cmd == "force_arm": self._do_arm_disarm(force=True)
                elif cmd == "set_mode": self._do_set_mode(data)
                elif cmd == "mission_start": self._do_mission_start()
                elif cmd == "abort_land": self._do_abort_land()
            except Empty:
                pass

            # Check for heartbeat timeout
            current_time = time.time()
            with self._lock:
                conn_exists = self._conn is not None
            
            if (conn_exists and current_time - last_heartbeat_check > HEARTBEAT_CHECK_INTERVAL_SEC):
                last_heartbeat_check = current_time
                with self._lock:
                    if (self._connected and current_time - self._last_heartbeat > HEARTBEAT_TIMEOUT):
                        self._connected = False
                        self._out_queue.put(("error", "Heartbeat timeout - connection lost"))
                        self._out_queue.put(("status", "Disconnected"))

            with self._lock:
                conn = self._conn
            
            if conn:
                try:
                    msg = conn.recv_match(blocking=False)
                    if msg: 
                        self._process_message(msg)
                except Exception as e:
                    self._out_queue.put(("error", f"Receive error: {e}"))
                    with self._lock:
                        self._conn = None
                        self._connected = False
                    self._out_queue.put(("status", "Disconnected"))
            time.sleep(WORKER_LOOP_SLEEP_SEC)

    def stop(self):
        self._running = False
        self._do_disconnect()

    def _do_connect(self):
        if not self._device: return self._out_queue.put(("error", "No device configured"))
        try:
            self._out_queue.put(("status", f"Connecting to {self._device} @ {self._baud}"))
            # Add connection timeout and better error handling
            self._conn = mavutil.mavlink_connection(
                self._device, 
                baud=self._baud, 
                autoreconnect=True,
                source_system=255,  # GCS system ID
                source_component=0   # GCS component ID,
            )
            
            # Implement better heartbeat timeout handling
            self._conn.wait_heartbeat(timeout=CONNECTION_TIMEOUT)
            
            with self._lock:
                self._connected = True
            self._last_heartbeat = time.time()
            self._out_queue.put(("status", "Connected"))
            
            # Request specific data streams instead of all data streams
            # This gives better control over bandwidth and data accuracy
            self._conn.mav.request_data_stream_send(
                self._conn.target_system, 
                self._conn.target_component, 
                mavutil.mavlink.MAV_DATA_STREAM_EXTENDED_STATUS, 2, 1)  # 2Hz
            self._conn.mav.request_data_stream_send(
                self._conn.target_system, 
                self._conn.target_component, 
                mavutil.mavlink.MAV_DATA_STREAM_POSITION, 10, 1)  # 10Hz
            self._conn.mav.request_data_stream_send(
                self._conn.target_system, 
                self._conn.target_component, 
                mavutil.mavlink.MAV_DATA_STREAM_EXTRA1, 10, 1)  # 10Hz for AHRS
            self._conn.mav.request_data_stream_send(
                self._conn.target_system, 
                self._conn.target_component, 
                mavutil.mavlink.MAV_DATA_STREAM_EXTRA2, 2, 1)  # 2Hz for VFR_HUD
        except Exception as e:
            self._out_queue.put(("error", f"Connection failed: {e}"))
            if self._conn: self._conn.close()
            with self._lock:
                self._conn = None
                self._connected = False

    def _do_disconnect(self):
        with self._lock:
            conn = self._conn
            self._conn = None
            self._connected = False
        
        if conn:
            try: 
                conn.close()
            except Exception as e:
                self._out_queue.put(("error", f"Error closing connection: {e}"))
        self._out_queue.put(("status", "Disconnected"))

    def _do_arm_disarm(self, force=False):
        if not self._conn: return self._out_queue.put(("error", "Not connected"))

        # Check armed status with lock
        is_armed = False
        with self._lock:
            is_armed = self._is_armed

        try:
            if is_armed:
                self._out_queue.put(("status", "Sending Disarm command..."))
                self._conn.mav.command_long_send(
                    self._conn.target_system, self._conn.target_component,
                    mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
                    0, 0, 0, 0, 0, 0, 0)
            else:
                if force:
                    self._out_queue.put(("status", "Sending Force Arm command..."))
                    self._conn.mav.command_long_send(
                        self._conn.target_system, self._conn.target_component,
                        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
                        1, 21196.0, 0, 0, 0, 0, 0)
                else:
                    self._out_queue.put(("status", "Sending Arm command..."))
                    self._conn.mav.command_long_send(
                        self._conn.target_system, self._conn.target_component,
                        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
                        1, 0, 0, 0, 0, 0, 0)
        except Exception as e:
            self._out_queue.put(("error", f"Failed to send Arm/Disarm command: {e}"))
            return

        # Check for acknowledgment
        try:
            ack = self._conn.recv_match(type='COMMAND_ACK', blocking=True, timeout=COMMAND_ACK_TIMEOUT_SEC)
            if ack and ack.command == mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM:
                if ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
                    self._out_queue.put(("status", "Arm/Disarm command accepted by FCU."))
                else:
                    result_name = "UNKNOWN"
                    if hasattr(mavutil.mavlink, 'enums') and 'MAV_RESULT' in mavutil.mavlink.enums:
                        result_name = mavutil.mavlink.enums['MAV_RESULT'].get(ack.result, "UNKNOWN")
                    self._out_queue.put(("error", f"Arm/Disarm command rejected: {result_name}"))
            else:
                self._out_queue.put(("error", "No acknowledgment for Arm/Disarm command."))
        except Exception as e:
            self._out_queue.put(("error", f"Failed to receive acknowledgment for Arm/Disarm command: {e}"))

    def _do_set_mode(self, mode_id):
        with self._lock:
            conn = self._conn
        
        if not conn: 
            return self._out_queue.put(("error", "Not connected"))
        
        self._out_queue.put(("status", f"Sending Set Mode command (Mode ID: {mode_id})..."))
        try:
            conn.mav.set_mode_send(conn.target_system, mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, mode_id)
            
            # Wait for mode change confirmation via heartbeat rather than COMMAND_ACK
            # SET_MODE doesn't always generate COMMAND_ACK, but mode change is reflected in heartbeat
            self._out_queue.put(("status", f"Set mode command sent for mode {mode_id}. Waiting for confirmation..."))
        except Exception as e:
            self._out_queue.put(("error", f"Failed to set mode: {e}"))

    def _do_mission_start(self):
        if not self._conn: return self._out_queue.put(("error", "Not connected"))
        self._out_queue.put(("status", "Sending Mission Start command (MAV_CMD_MISSION_START)..."))
        try:
            self._conn.mav.command_long_send(
                self._conn.target_system, self._conn.target_component,
                mavutil.mavlink.MAV_CMD_MISSION_START, 0,
                0, 0, 0, 0, 0, 0, 0)
            self._out_queue.put(("status", "Mission Start command sent."))
        except Exception as e:
            self._out_queue.put(("error", f"Failed to send mission start: {e}"))

    def _do_abort_land(self):
        if not self._conn: return self._out_queue.put(("error", "Not connected"))
        self._out_queue.put(("status", "Sending Abort Landing command (MAV_CMD_NAV_RETURN_TO_LAUNCH)..."))
        try:
            self._conn.mav.command_long_send(
                self._conn.target_system, self._conn.target_component,
                mavutil.mavlink.MAV_CMD_NAV_RETURN_TO_LAUNCH, 0,
                0, 0, 0, 0, 0, 0, 0)
            self._out_queue.put(("status", "Abort Landing (RTL) command sent."))
        except Exception as e:
            self._out_queue.put(("error", f"Failed to send abort command: {e}"))

    def get_data_quality(self):
        """Return current data quality metrics"""
        with self._lock:
            return {
                "connected": self._connected,
                "data_rates": self._data_rates.copy(),
                "message_counts": self._message_counts.copy()
            }

    def _process_message(self, msg):
        mtype = msg.get_type()
        
        # Track message rates
        current_time = time.time()
        if mtype not in self._message_counts:
            self._message_counts[mtype] = 0
            self._last_message_time[mtype] = current_time
        
        self._message_counts[mtype] += 1
        
        # Calculate data rate (messages per second)
        if current_time - self._last_message_time[mtype] > DATA_RATE_CALCULATION_INTERVAL_SEC:
            elapsed = current_time - self._last_message_time[mtype]
            self._data_rates[mtype] = self._message_counts[mtype] / elapsed
            # Reset counters
            self._message_counts[mtype] = 0
            self._last_message_time[mtype] = current_time
            
            # Send data rate info for critical messages
            if mtype in ["ATTITUDE", "VFR_HUD", "GPS_RAW_INT"]:
                self._out_queue.put(("data_rate", {mtype: self._data_rates[mtype]}))
        
        # Add timestamp for data freshness tracking
        timestamp = current_time
        
        if mtype == "HEARTBEAT":
            # Validate heartbeat data
            if not hasattr(msg, 'type') or not hasattr(msg, 'autopilot'):
                return  # Invalid heartbeat
                
            self._last_heartbeat = timestamp
            with self._lock:
                self._is_armed = (msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED) != 0
            
            # Get flight mode
            mode_id = msg.custom_mode
            if self._conn and self._conn.mode_mapping():
                mode = self._conn.mode_mapping().get(mode_id)
                if mode:
                    self._out_queue.put(("flight_mode", mode))
        elif mtype == "STATUSTEXT":
            text = msg.text
            if isinstance(text, bytes):
                text = text.decode(errors="ignore")
            self._out_queue.put(("statustext", text))
        elif mtype == "ATTITUDE":
            # Validate attitude data
            if (hasattr(msg, 'roll') and hasattr(msg, 'pitch') and hasattr(msg, 'yaw') and
                math.isfinite(msg.roll) and math.isfinite(msg.pitch) and math.isfinite(msg.yaw) and
                abs(msg.roll) <= math.pi and abs(msg.pitch) <= math.pi and abs(msg.yaw) <= math.pi):
                self._out_queue.put(("attitude", {
                    "timestamp": timestamp,
                    "roll": msg.roll, 
                    "pitch": msg.pitch, 
                    "yaw": msg.yaw
                }))
        elif mtype == "VFR_HUD":
            # Validate VFR_HUD data
            if (hasattr(msg, 'airspeed') and hasattr(msg, 'groundspeed') and hasattr(msg, 'alt') and hasattr(msg, 'heading') and
                math.isfinite(msg.airspeed) and math.isfinite(msg.groundspeed) and math.isfinite(msg.alt) and math.isfinite(msg.heading) and
                msg.airspeed >= 0 and msg.groundspeed >= 0 and 0 <= msg.heading <= 360):
                self._out_queue.put(("vfr_hud", {
                    "timestamp": timestamp,
                    "airspeed": msg.airspeed, 
                    "groundspeed": msg.groundspeed, 
                    "alt": msg.alt, 
                    "heading": msg.heading
                }))
        elif mtype == "GPS_RAW_INT":
            # Validate GPS data
            if (hasattr(msg, 'fix_type') and hasattr(msg, 'satellites_visible') and 
                hasattr(msg, 'lat') and hasattr(msg, 'lon') and hasattr(msg, 'eph') and hasattr(msg, 'epv') and
                msg.fix_type >= 0 and msg.satellites_visible >= 0):
                
                lat = msg.lat / 1e7
                lon = msg.lon / 1e7
                hdop = msg.eph / 100.0 if msg.eph != 65535 else -1
                vdop = msg.epv / 100.0 if msg.epv != 65535 else -1
                
                # Validate coordinates are finite and within valid range
                if (math.isfinite(lat) and math.isfinite(lon) and 
                    -90 <= lat <= 90 and -180 <= lon <= 180):
                    self._out_queue.put(("gps", {
                        "timestamp": timestamp,
                        "fix_type": msg.fix_type, 
                        "satellites": msg.satellites_visible, 
                        "lat": lat, 
                        "lon": lon, 
                        "hdop": hdop, 
                        "vdop": vdop
                    }))
        elif mtype == "GLOBAL_POSITION_INT":
            # Validate global position data
            if (hasattr(msg, 'lat') and hasattr(msg, 'lon') and hasattr(msg, 'relative_alt')):
                lat = msg.lat / 1e7
                lon = msg.lon / 1e7
                alt = msg.relative_alt / 1000.0
                
                # Validate data is finite and within valid range
                if (math.isfinite(lat) and math.isfinite(lon) and math.isfinite(alt) and
                    -90 <= lat <= 90 and -180 <= lon <= 180):
                    self._out_queue.put(("gps_pos", {
                        "timestamp": timestamp,
                        "lat": lat, 
                        "lon": lon, 
                        "alt": alt
                    }))
        elif mtype == "SYS_STATUS":
            # Validate system status data
            if (hasattr(msg, 'voltage_battery') and hasattr(msg, 'current_battery') and hasattr(msg, 'battery_remaining')):
                voltage = msg.voltage_battery / 1000.0
                current = msg.current_battery / 100.0
                remaining = msg.battery_remaining
                
                # Validate data is finite and within reasonable range
                if (math.isfinite(voltage) and math.isfinite(current) and 
                    voltage >= 0 and current >= -100 and 0 <= remaining <= 100):
                    self._out_queue.put(("sys_status", {
                        "timestamp": timestamp,
                        "voltage": voltage, 
                        "current": current, 
                        "remaining": remaining
                    }))
        else:
            self._out_queue.put(("debug", f"{mtype}: {msg}"))