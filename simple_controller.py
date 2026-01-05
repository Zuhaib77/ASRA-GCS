"""
ASRA GCS v2.0 - Simple Controller Wrapper
Simplified controller for multi-drone that just polls telemetry
Connection management is handled by DroneManager
"""

from PyQt5.QtCore import QTimer

class SimpleController:
    """
    Simplified controller for v2.0 multi-drone
    Only handles telemetry polling - connection managed by DroneManager
    """
    
    def __init__(self, panel, worker):
        self.panel = panel
        self.worker = worker
        
        # Don't need timer - main_window handles update loop
        
    def update_ui(self):
        """Poll worker and update UI with telemetry"""
        if not self.worker:
            return
            
        # Get all updates from worker queue
        try:
            updates = self.worker.get_updates()
        except Exception as e:
            print(f"Error getting updates: {e}")
            return
        
        for msg_type, data in updates:
            try:
                # Ensure data is a dict
                if not isinstance(data, dict):
                    continue
                    
                # Route to panel's telemetry update via drone manager
                self.panel.drone_manager.update_telemetry(
                    self.panel.drone_id,
                    msg_type,
                    data
                )
            except Exception as e:
                print(f"Error processing telemetry {msg_type}: {e}")
