import os
import logging
from datetime import datetime
from PyQt5 import QtCore, QtWidgets

# Import optimized configuration
try:
    from config import config, UI_UPDATE_RATE, BUTTON_FEEDBACK_DURATION
    from performance_monitor import PerformanceMonitor, monitor_ui_update
    from logging_config import get_logger
except ImportError:
    # Fallback for standalone use
    config = None
    UI_UPDATE_RATE = 150
    BUTTON_FEEDBACK_DURATION = 200
    PerformanceMonitor = None
    get_logger = logging.getLogger

class Controller(QtCore.QObject):
    def __init__(self, ui, worker):
        super().__init__()
        self.ui = ui
        self.worker = worker
        self.logger = get_logger("controller")
        
        # Performance monitoring (don't auto-start to prevent threading issues)
        self.performance_monitor = PerformanceMonitor(config) if PerformanceMonitor else None
        # Note: Performance monitor start moved to after UI is fully loaded

        # ArduPilot Copter specific modes
        self.mode_mapping = {
            "Stabilize": 0,
            "Alt Hold": 2,
            "Loiter": 5,
            "RTL": 6,
            "Land": 9,
            "Auto": 3, # Mission
            "Guided": 4
        }
        self.fix_suggestions = {
            "PreArm": "Suggestion: Check sensors, GPS lock, and arming checks.",
            "GPS": "Suggestion: Ensure clear sky view for GPS lock.",
            "failsafe": "Suggestion: Check RC connection and battery levels.",
            "compass": "Suggestion: Calibrate compass away from magnetic interference."
        }

        # Connect signals for main controls
        ui.btn_connect.clicked.connect(self.on_connect)
        ui.btn_disconnect.clicked.connect(self.on_disconnect)
        ui.refresh_btn.clicked.connect(self.refresh_ports)
        
        # Connect vehicle control signals
        ui.btn_arm_disarm.clicked.connect(self.on_arm_disarm)
        ui.btn_set_mode.clicked.connect(self.on_set_mode)
        ui.btn_force_arm.clicked.connect(self.on_force_arm)
        ui.btn_mission_start.clicked.connect(self.on_mission_start)
        ui.btn_abort_land.clicked.connect(self.on_abort_land)
        

        self.refresh_ports()
        ui.btn_disconnect.setEnabled(False)

        # Telemetry throttling for performance
        self.telemetry_throttle = {}
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self._update_ui_with_monitoring)
        self.timer.start(UI_UPDATE_RATE)

    def refresh_ports(self):
        ports = []
        try:
            import serial.tools.list_ports
            ports = [f"{p.device} - {p.description}" for p in serial.tools.list_ports.comports()]
        except Exception as e:
            ports = ["No ports detected"]
        self.ui.set_ports(ports)

    def on_connect(self):
        if not self.worker.is_alive():
            try: self.worker.start()
            except RuntimeError: pass
        port, baud = self.ui.get_port_and_baud()
        if not port or "No ports" in port:
            self.ui.append_message("<font color='red'>Error: No valid port selected</font>")
            return
        device = port.split(' - ')[0].strip()
        self.worker.configure(device, baud)
        self.worker.connect()
        self.ui.append_message(f"Connecting to {device} @ {baud}...")

    def on_disconnect(self):
        self.worker.disconnect()
        self.ui.append_message("Disconnecting...")

    def on_arm_disarm(self):
        self.ui.append_message("Sending Arm/Disarm command...")
        # Visual feedback for button press
        self.ui.btn_arm_disarm.setStyleSheet("background-color: #777;")
        QtCore.QTimer.singleShot(BUTTON_FEEDBACK_DURATION, lambda: self.ui.btn_arm_disarm.setStyleSheet(""))
        self.worker.arm_disarm()

    def on_set_mode(self):
        mode_name = self.ui.combo_modes.currentText()
        mode_id = self.mode_mapping.get(mode_name)
        if mode_id is not None:
            self.ui.append_message(f"Setting mode to {mode_name}...")
            # Visual feedback for button press
            self.ui.btn_set_mode.setStyleSheet("background-color: #777;")
            QtCore.QTimer.singleShot(BUTTON_FEEDBACK_DURATION, lambda: self.ui.btn_set_mode.setStyleSheet(""))
            self.worker.set_mode(mode_id)
        else:
            self.ui.append_message(f"<font color='red'>Error: Unknown mode '{mode_name}'</font>")

    def on_force_arm(self):
        # Confirmation dialog for force arm
        reply = QtWidgets.QMessageBox.question(
            self.ui, "Confirm Force Arm", 
            "Are you sure you want to force arm the vehicle? This bypasses safety checks and should only be used in emergencies.",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            self.ui.append_message("Sending Force Arm command...")
            # Visual feedback for button press
            self.ui.btn_force_arm.setStyleSheet("background-color: #777;")
            QtCore.QTimer.singleShot(BUTTON_FEEDBACK_DURATION, lambda: self.ui.btn_force_arm.setStyleSheet(""))
            self.worker.force_arm()
        else:
            self.ui.append_message("Force Arm cancelled.")

    def on_mission_start(self):
        # Confirmation dialog for mission start
        reply = QtWidgets.QMessageBox.question(
            self.ui, "Confirm Mission Start", 
            "Are you sure you want to start the mission? This will begin autonomous flight.",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            self.ui.append_message("Sending Mission Start command...")
            # Visual feedback for button press
            self.ui.btn_mission_start.setStyleSheet("background-color: #777;")
            QtCore.QTimer.singleShot(BUTTON_FEEDBACK_DURATION, lambda: self.ui.btn_mission_start.setStyleSheet(""))
            self.worker.mission_start()
        else:
            self.ui.append_message("Mission Start cancelled.")

    def on_abort_land(self):
        # Confirmation dialog for abort landing
        reply = QtWidgets.QMessageBox.question(
            self.ui, "Confirm Abort Landing", 
            "Are you sure you want to abort landing and return to launch? This will interrupt the landing sequence.",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            self.ui.append_message("Sending Abort Landing command...")
            # Visual feedback for button press
            self.ui.btn_abort_land.setStyleSheet("background-color: #777;")
            QtCore.QTimer.singleShot(BUTTON_FEEDBACK_DURATION, lambda: self.ui.btn_abort_land.setStyleSheet(""))
            self.worker.abort_land()
        else:
            self.ui.append_message("Abort Landing cancelled.")

    def _provide_fix_suggestion(self, text):
        """Provide fix suggestions in the Messages tab along with FCU messages"""
        for keyword, suggestion in self.fix_suggestions.items():
            if keyword.lower() in text.lower():
                self.ui.append_message(f"<font color='yellow'>{suggestion}</font>")

    def _update_ui_with_monitoring(self):
        """UI update wrapper with performance monitoring"""
        if self.performance_monitor:
            import time
            start_time = time.time()
            try:
                self.update_ui()
            finally:
                end_time = time.time()
                self.performance_monitor.log_ui_update_time((end_time - start_time) * 1000)
        else:
            self.update_ui()
    
    def update_ui(self):
        # Update connection and armed status in HUD
        self.ui.hud.update_connection_status(self.worker.is_connected())
        self.ui.hud.update_armed_status(self.worker.is_armed())
        
        updates = self.worker.get_updates()
        if not updates:
            return  # No updates, nothing to do
            
        for msg_type, data in updates:
            if msg_type == "status":
                # Application status messages
                self.ui.append_message(data)
                if data == "Connected":
                    self.ui.btn_connect.setEnabled(False)
                    self.ui.btn_disconnect.setEnabled(True)
                    self.ui.append_message("<font color='green'>Successfully connected to vehicle.</font>")
                elif data == "Disconnected":
                    self.ui.btn_connect.setEnabled(True)
                    self.ui.btn_disconnect.setEnabled(False)
                    self.ui.append_message("<font color='green'>Disconnected from vehicle.</font>")
            elif msg_type == "error":
                # Application errors
                self.ui.append_message(f"<font color='red'>Error: {data}</font>")
            elif msg_type == "success":
                # Application success messages
                self.ui.append_message(f"<font color='green'>Success: {data}</font>")
            elif msg_type == "statustext":
                # FCU STATUSTEXT messages
                # Color-code different types of status messages
                if "error" in data.lower() or "fail" in data.lower():
                    self.ui.append_message(f"<font color='red'>FCU: {data}</font>")
                elif "warning" in data.lower():
                    self.ui.append_message(f"<font color='orange'>FCU: {data}</font>")
                else:
                    self.ui.append_message(f"<font color='cyan'>FCU: {data}</font>")
                self._provide_fix_suggestion(data)
            elif msg_type == "attitude":
                self.ui.update_attitude(data.get('roll',0), data.get('pitch',0), data.get('yaw',0))
            elif msg_type == "vfr_hud":
                self.ui.update_hud(data.get('airspeed',0), data.get('groundspeed',0), data.get('alt',0), data.get('heading',0))
            elif msg_type == "gps":
                self.ui.update_gps(data.get('fix_type',0), data.get('satellites',0), data.get('hdop',0), data.get('vdop',0), data.get('lat',0), data.get('lon',0))
            elif msg_type == "sys_status":
                self.ui.update_status(data.get('voltage',0), data.get('current',0), data.get('remaining',-1))
            elif msg_type == "gps_pos":
                self.ui.update_position(data.get('lat',0), data.get('lon',0), data.get('alt',0))
            elif msg_type == "flight_mode":
                self.ui.update_flight_mode(data)
                self.ui.append_message(f"<font color='green'>Flight mode changed to: {data}</font>")
