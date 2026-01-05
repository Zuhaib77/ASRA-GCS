"""
ASRA GCS - Multi-Drone Connection Manager
Manages multiple simultaneous drone connections for v2.0
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from PyQt5.QtCore import QObject, pyqtSignal
from mavlink_worker import MavlinkWorker

try:
    from logging_config import get_logger
except ImportError:
    get_logger = logging.getLogger


@dataclass
class DroneConnection:
    """Represents a single drone connection"""
    drone_id: str                    # Unique identifier (e.g., "drone_1", "drone_2")
    name: str                        # User-friendly name (e.g., "COM3", "Alpha")
    port: str                        # Connection port/address
    baud: int                        # Baud rate
    worker: MavlinkWorker           # MAVLink worker thread
    color: str                       # UI color (auto-assigned)
    connected: bool = False
    armed: bool = False
    telemetry: Dict = field(default_factory=dict)  # Latest telemetry data
    
    def __post_init__(self):
        """Initialize telemetry with default values"""
        if not self.telemetry:
            self.telemetry = {
                'attitude': {'roll': 0, 'pitch': 0, 'yaw': 0},
                'position': {'lat': 0, 'lon': 0, 'alt': 0},
                'gps': {'fix_type': 0, 'satellites': 0, 'hdop': 0, 'vdop': 0},
                'battery': {'voltage': 0, 'current': 0, 'remaining': -1},
                'flight_mode': 'Unknown',
                'last_update': 0
            }


class DroneManager(QObject):
    """
    Manages multiple drone connections
    Coordinates MAVLink workers and routes telemetry to UI
    """
    
    # Signals for UI updates
    drone_added = pyqtSignal(str)              # drone_id
    drone_removed = pyqtSignal(str)            # drone_id
    drone_connected = pyqtSignal(str)          # drone_id
    drone_disconnected = pyqtSignal(str)       # drone_id
    drone_telemetry_updated = pyqtSignal(str, str, dict)  # drone_id, msg_type, data
    
    # Default drone colors (auto-assigned)
    DEFAULT_COLORS = [
        "#FF0000",  # Red
        "#0000FF",  # Blue
        "#00FF00",  # Green
        "#FFFF00",  # Yellow
        "#FF00FF",  # Magenta
        "#00FFFF",  # Cyan
    ]
    
    def __init__(self, max_drones: int = 2):
        super().__init__()
        self.max_drones = max_drones
        self.drones: Dict[str, DroneConnection] = {}
        self.logger = get_logger("drone_manager")
        self._next_drone_number = 1
        
        self.logger.info(f"DroneManager initialized (max drones: {max_drones})")
    
    def add_drone(self, port: str, baud: int, name: Optional[str] = None) -> Optional[str]:
        """
        Add a new drone connection
        
        Args:
            port: COM port or connection string (e.g., "COM3", "udp:127.0.0.1:14550")
            baud: Baud rate
            name: Optional custom name (defaults to auto-generated)
            
        Returns:
            drone_id if successful, None if max drones reached
        """
        # Check if we've reached max drones
        if len(self.drones) >= self.max_drones:
            self.logger.warning(f"Cannot add drone: max drones ({self.max_drones}) reached")
            return None
        
        # Generate drone ID and name
        drone_id = f"drone_{self._next_drone_number}"
        self._next_drone_number += 1
        
        if name is None:
            name = port.split(' - ')[0] if ' - ' in port else port
        
        # Assign color
        color_index = len(self.drones) % len(self.DEFAULT_COLORS)
        color = self.DEFAULT_COLORS[color_index]
        
        # Create MAVLink worker
        worker = MavlinkWorker()
        worker.configure(port.split(' - ')[0] if ' - ' in port else port, baud)
        
        # Create drone connection
        drone = DroneConnection(
            drone_id=drone_id,
            name=name,
            port=port,
            baud=baud,
            worker=worker,
            color=color
        )
        
        # Store drone
        self.drones[drone_id] = drone
        
        self.logger.info(f"Added drone: {drone_id} ({name}) on {port} @ {baud} baud - Color: {color}")
        
        # Emit signal
        self.drone_added.emit(drone_id)
        
        return drone_id
    
    def remove_drone(self, drone_id: str) -> bool:
        """
        Remove a drone connection
        
        Args:
            drone_id: Drone identifier
            
        Returns:
            True if removed successfully, False if not found
        """
        if drone_id not in self.drones:
            self.logger.warning(f"Cannot remove drone: {drone_id} not found")
            return False
        
        drone = self.drones[drone_id]
        
        # Disconnect if connected
        if drone.connected:
            drone.worker.disconnect()
        
        # Stop worker thread
        drone.worker.stop()
        
        # Remove from dict
        del self.drones[drone_id]
        
        self.logger.info(f"Removed drone: {drone_id}")
        
        # Emit signal
        self.drone_removed.emit(drone_id)
        
        return True
    
    def connect_drone(self, drone_id: str) -> bool:
        """
        Connect to a drone
        
        Args:
            drone_id: Drone identifier
            
        Returns:
            True if connection initiated, False if not found
        """
        if drone_id not in self.drones:
            self.logger.warning(f"Cannot connect: drone {drone_id} not found")
            return False
        
        drone = self.drones[drone_id]
        
        # Start worker thread if not running
        if not drone.worker.is_alive():
            try:
                drone.worker.start()
            except RuntimeError:
                pass  # Thread already started
        
        # Connect
        drone.worker.connect()
        drone.connected = True
        
        self.logger.info(f"Connecting drone: {drone_id}")
        
        # Emit signal
        self.drone_connected.emit(drone_id)
        
        return True
    
    def disconnect_drone(self, drone_id: str) -> bool:
        """
        Disconnect from a drone
        
        Args:
            drone_id: Drone identifier
            
        Returns:
            True if disconnected, False if not found
        """
        if drone_id not in self.drones:
            self.logger.warning(f"Cannot disconnect: drone {drone_id} not found")
            return False
        
        drone = self.drones[drone_id]
        drone.worker.disconnect()
        drone.connected = False
        drone.armed = False
        
        self.logger.info(f"Disconnected drone: {drone_id}")
        
        # Emit signal
        self.drone_disconnected.emit(drone_id)
        
        return True
    
    def get_drone(self, drone_id: str) -> Optional[DroneConnection]:
        """Get drone connection by ID"""
        return self.drones.get(drone_id)
    
    def get_all_drones(self) -> List[DroneConnection]:
        """Get all drone connections"""
        return list(self.drones.values())
    
    def get_drone_count(self) -> int:
        """Get number of drones"""
        return len(self.drones)
    
    def can_add_drone(self) -> bool:
        """Check if another drone can be added"""
        return len(self.drones) < self.max_drones
    
    def update_telemetry(self, drone_id: str, msg_type: str, data: dict):
        """
        Update telemetry for a specific drone
        Called by controller after polling worker queues
        
        Args:
            drone_id: Drone identifier
            msg_type: Message type (e.g., 'attitude', 'gps', 'battery')
            data: Telemetry data dict
        """
        if drone_id not in self.drones:
            return
        
        drone = self.drones[drone_id]
        
        # Update telemetry storage
        if msg_type in drone.telemetry:
            drone.telemetry[msg_type].update(data)
        else:
            drone.telemetry[msg_type] = data
        
        # Update armed status
        if msg_type == 'status':
            if 'armed' in data:
                drone.armed = data['armed']
        
        # Emit signal for UI update
        self.drone_telemetry_updated.emit(drone_id, msg_type, data)
    
    def get_telemetry(self, drone_id: str, msg_type: Optional[str] = None) -> Optional[dict]:
        """
        Get telemetry data for a drone
        
        Args:
            drone_id: Drone identifier
            msg_type: Specific message type, or None for all telemetry
            
        Returns:
            Telemetry dict or None if not found
        """
        if drone_id not in self.drones:
            return None
        
        drone = self.drones[drone_id]
        
        if msg_type is None:
            return drone.telemetry
        else:
            return drone.telemetry.get(msg_type)
    
    def send_command(self, drone_id: str, command: str, *args, **kwargs):
        """
        Send command to specific drone
        
        Args:
            drone_id: Drone identifier
            command: Command name (e.g., 'arm_disarm', 'set_mode')
            *args, **kwargs: Command arguments
        """
        if drone_id not in self.drones:
            self.logger.warning(f"Cannot send command: drone {drone_id} not found")
            return
        
        drone = self.drones[drone_id]
        
        # Call appropriate worker method
        if hasattr(drone.worker, command):
            method = getattr(drone.worker, command)
            method(*args, **kwargs)
            self.logger.debug(f"Sent command '{command}' to drone {drone_id}")
        else:
            self.logger.warning(f"Unknown command: {command}")
    
    def cleanup(self):
        """Cleanup all drone connections"""
        self.logger.info("Cleaning up all drone connections...")
        
        for drone_id in list(self.drones.keys()):
            self.remove_drone(drone_id)
        
        self.logger.info("Cleanup complete")
