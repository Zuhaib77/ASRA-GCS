"""
ASRA GCS v2.0 - Simple Controller Wrapper
Simplified controller for multi-drone that polls telemetry
Connection management is handled by DroneManager
"""

from PyQt5.QtCore import QTimer

class SimpleController:
    """
    Simplified controller for v2.0 multi-drone
    Handles telemetry polling - connection managed by DroneManager
    """
    
    def __init__(self, panel, worker, drone_manager, drone_id):
        self.panel = panel
        self.worker = worker
        self.drone_manager = drone_manager
        self.drone_id = drone_id
        
    def update_ui(self):
        """Poll worker and update UI with telemetry"""
        if not self.worker:
            return
            
        # Get all updates from worker queue
        try:
            updates = self.worker.get_updates()
        except Exception as e:
            print(f"Error getting updates from worker: {e}")
            return
        
        for msg_type, data in updates:
            try:
                # Handle different message types
                if msg_type == "status":
                    # Connection status message (string)
                    self._handle_status(data)
                elif msg_type == "error":
                    # Error message (string)
                    self._handle_error(data)
                elif msg_type == "flight_mode":
                    # Flight mode (string)
                    self.drone_manager.update_telemetry(
                        self.drone_id, 'flight_mode', {'mode': data}
                    )
                elif msg_type == "statustext":
                    # Status text from FCU (string)
                    self._handle_statustext(data)
                elif isinstance(data, dict):
                    # Telemetry data (dict) - attitude, gps, vfr_hud, etc.
                    self.drone_manager.update_telemetry(
                        self.drone_id,
                        msg_type,
                        data
                    )
                # else: ignore debug or unknown messages
                    
            except Exception as e:
                print(f"Error processing {msg_type}: {e}")
    
    def _handle_status(self, status_text):
        """Handle connection status updates"""
        drone = self.drone_manager.get_drone(self.drone_id)
        if not drone:
            return
            
        if "Connected" in status_text:
            drone.connected = True
            self.drone_manager.drone_connected.emit(self.drone_id)
        elif "Disconnected" in status_text:
            drone.connected = False
            drone.armed = False
            self.drone_manager.drone_disconnected.emit(self.drone_id)
        
        # Update telemetry with status
        self.drone_manager.update_telemetry(
            self.drone_id, 'status_message', {'text': status_text}
        )
    
    def _handle_error(self, error_text):
        """Handle error messages"""
        self.drone_manager.update_telemetry(
            self.drone_id, 'error_message', {'text': error_text}
        )
    
    def _handle_statustext(self, text):
        """Handle FCU status text"""
        self.drone_manager.update_telemetry(
            self.drone_id, 'fcu_statustext', {'text': text}
        )
