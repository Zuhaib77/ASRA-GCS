import math
from PyQt5 import QtCore, QtGui, QtWidgets
from hud_widget_reference_style import ReferenceStyleHUDWidget
from controller import Controller
from mavlink_worker import MavlinkWorker
from logger import TelemetryLogger

class ASRAGCS_UI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ASRA GCS - Advanced Ground Control Station")
        self.resize(1600, 1000)  # Larger default size for better map visibility
        # Simple, stable styling
        self.setStyleSheet("""
            QWidget {
                background-color: #2a2a2a;
                color: #ffffff;
                font-family: Arial, sans-serif;
                font-size: 9pt;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: #333333;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 8px;
                color: #00aaff;
            }
            QPushButton {
                background-color: #0078d4;
                border: 1px solid #005a9e;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                color: white;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #404040;
                color: #808080;
            }
            QComboBox {
                background-color: #404040;
                border: 1px solid #555555;
                padding: 6px 12px;
                border-radius: 4px;
                min-width: 100px;
            }
            QTextEdit {
                background-color: #1a1a1a;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 8px;
                font-family: Consolas, monospace;
                font-size: 9pt;
            }
            QLabel {
                color: #ffffff;
            }
        """)

        # Main grid layout (restore original design)
        main_layout = QtWidgets.QGridLayout(self)

        # HUD widget (left side - larger)
        self.hud = ReferenceStyleHUDWidget(self)
        # Optimize HUD size while keeping proportions
        self.hud.setFixedSize(480, 400)  # Increased from original 350x300, maintaining 1.2:1 ratio
        main_layout.addWidget(self.hud, 0, 0, 1, 1)

        # Map widget (center - prominent position)
        self.map_widget = self._create_offline_map_widget()
        main_layout.addWidget(self.map_widget, 0, 1, 1, 1)

        # Right panel for telemetry and actions
        right_panel = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_panel)
        attitude_box = self._create_telemetry_groupbox("Attitude", [("Roll","lbl_roll"), ("Pitch","lbl_pitch"), ("Yaw","lbl_yaw"), ("Mode","lbl_mode")])
        gps_box = self._create_telemetry_groupbox("GPS", [("Fix Type","lbl_gps_fix"), ("Satellites","lbl_gps_sats"), ("HDOP","lbl_gps_hdop"), ("VDOP","lbl_gps_vdop"), ("Latitude","lbl_gps_lat"), ("Longitude","lbl_gps_lon")])
        status_box = self._create_telemetry_groupbox("System Status", [("Voltage","lbl_status_volt"), ("Current","lbl_status_curr"), ("Battery","lbl_status_rem")])
        actions_box = self._create_actions_groupbox()
        right_layout.addWidget(attitude_box)
        right_layout.addWidget(gps_box)
        right_layout.addWidget(status_box)
        right_layout.addWidget(actions_box)
        right_layout.addStretch()
        main_layout.addWidget(right_panel, 0, 2, 1, 1)

        # Bottom panel for connection, logs and messages
        bottom_panel = self._create_bottom_panel()
        main_layout.addLayout(bottom_panel, 1, 0, 1, 3)

        main_layout.setColumnStretch(0, 2)  # HUD takes 2/5 of space
        main_layout.setColumnStretch(1, 2)  # Map takes 2/5 of space
        main_layout.setColumnStretch(2, 1)  # Right column takes 1/5
        main_layout.setRowStretch(0, 3)  # Top row takes 3/4 of space
        main_layout.setRowStretch(1, 1)  # Bottom row takes 1/4 of space

        # Initialize telemetry data
        self.airspeed = 0.0
        self.groundspeed = 0.0
        self.alt = 0.0
        self.yaw = 0.0
        self.current_mode = "Unknown"
        
        # Initialize MAVLink worker and controller with error handling
        try:
            self.logger = TelemetryLogger()
            self.mavlink_worker = MavlinkWorker()
            self.controller = Controller(self, self.mavlink_worker)
            print("ASRA GCS UI initialized successfully")
        except Exception as e:
            print(f"Warning: Some components failed to initialize: {e}")
            # Create dummy objects to prevent crashes
            self.logger = None
            self.mavlink_worker = None
            self.controller = None
        
    def _create_offline_map_widget(self):
        """Create professional GCS map widget like Mission Planner/QGroundControl"""
        try:
            from professional_gcs_map import ProfessionalGCSMap
            map_widget = ProfessionalGCSMap()
            return map_widget
        except Exception as e:
            print(f"Warning: Map widget failed to initialize: {e}")
            # Create a simple placeholder widget
            placeholder = QtWidgets.QLabel("Map Widget\n(Loading...)")
            placeholder.setStyleSheet("background-color: #2a2a2a; color: white; font-size: 16px; padding: 20px;")
            placeholder.setAlignment(QtCore.Qt.AlignCenter)
            return placeholder
        
    def _create_actions_groupbox(self):
        box = QtWidgets.QGroupBox("Vehicle Actions")
        layout = QtWidgets.QGridLayout(box)
        self.btn_arm_disarm = QtWidgets.QPushButton("Arm / Disarm")
        self.btn_force_arm = QtWidgets.QPushButton("Force Arm")
        self.combo_modes = QtWidgets.QComboBox()
        self.combo_modes.addItems(["Stabilize", "Alt Hold", "Loiter", "Auto", "Guided", "RTL", "Land"])
        self.btn_set_mode = QtWidgets.QPushButton("Set Mode")
        self.btn_mission_start = QtWidgets.QPushButton("Start Mission")
        self.btn_abort_land = QtWidgets.QPushButton("Abort Landing")
        layout.addWidget(self.btn_arm_disarm, 0, 0)
        layout.addWidget(self.btn_force_arm, 0, 1)
        layout.addWidget(self.combo_modes, 1, 0)
        layout.addWidget(self.btn_set_mode, 1, 1)
        layout.addWidget(self.btn_mission_start, 2, 0)
        layout.addWidget(self.btn_abort_land, 2, 1)
        return box

    def _create_telemetry_groupbox(self, title, labels):
        box = QtWidgets.QGroupBox(title)
        layout = QtWidgets.QGridLayout(box)
        tooltip_map = {
            "Roll": "Vehicle roll angle in degrees (rotation around longitudinal axis)",
            "Pitch": "Vehicle pitch angle in degrees (rotation around lateral axis)", 
            "Yaw": "Vehicle yaw angle in degrees (rotation around vertical axis)",
            "Mode": "Current flight mode of the vehicle",
            "Fix Type": "GPS fix quality (No GPS, No Fix, 2D, 3D, DGPS, RTK)",
            "Satellites": "Number of GPS satellites currently tracked",
            "HDOP": "Horizontal Dilution of Precision - GPS position accuracy",
            "VDOP": "Vertical Dilution of Precision - GPS altitude accuracy",
            "Latitude": "Vehicle latitude in decimal degrees",
            "Longitude": "Vehicle longitude in decimal degrees",
            "Voltage": "Battery voltage in volts",
            "Current": "Battery current draw in amperes",
            "Battery": "Remaining battery capacity as percentage"
        }
        for i, (text, name) in enumerate(labels):
            label = QtWidgets.QLabel(f"{text}:")
            value_label = QtWidgets.QLabel("N/A")
            setattr(self, name, value_label)
            layout.addWidget(label, i, 0)
            layout.addWidget(value_label, i, 1)
        return box

    def _create_bottom_panel(self):
        panel_layout = QtWidgets.QHBoxLayout()
        conn_box = QtWidgets.QGroupBox("Connection")
        conn_layout = QtWidgets.QHBoxLayout(conn_box)
        self.btn_connect = QtWidgets.QPushButton("Connect")
        self.btn_disconnect = QtWidgets.QPushButton("Disconnect")
        self.refresh_btn = QtWidgets.QPushButton("Refresh")
        self.port_combo = QtWidgets.QComboBox()
        self.baud_combo = QtWidgets.QComboBox()
        self.baud_combo.addItems(["57600", "115200", "230400"])
        conn_layout.addWidget(self.port_combo)
        conn_layout.addWidget(self.baud_combo)
        conn_layout.addWidget(self.refresh_btn)
        conn_layout.addWidget(self.btn_connect)
        conn_layout.addWidget(self.btn_disconnect)

        # Messages Panel (FCU Messages only - like Mission Planner)
        message_box = QtWidgets.QGroupBox("Messages")
        message_layout = QtWidgets.QVBoxLayout(message_box)
        self.message_area = QtWidgets.QTextEdit()
        self.message_area.setReadOnly(True)
        self.message_area.setFont(QtGui.QFont("Consolas", 9))
        message_layout.addWidget(self.message_area)

        panel_layout.addWidget(conn_box)
        panel_layout.addWidget(message_box, 1)
        return panel_layout





    def append_message(self, msg):
        """Append FCU message to Messages area (STATUSTEXT messages from flight controller)"""
        self.message_area.append(msg)

    def set_ports(self, ports):
        self.port_combo.clear()
        self.port_combo.addItems(ports)

    def get_port_and_baud(self):
        return self.port_combo.currentText(), int(self.baud_combo.currentText())

    def update_flight_mode(self, mode):
        self.lbl_mode.setText(mode)
        self.hud.update_flight_mode(mode)

    def update_attitude(self, roll, pitch, yaw):
        try:
            if hasattr(self, 'hud') and self.hud:
                self.hud.update_attitude(roll, pitch, yaw)
            if hasattr(self, 'lbl_roll'):
                self.lbl_roll.setText(f"{math.degrees(roll):.2f}°")
            if hasattr(self, 'lbl_pitch'):
                self.lbl_pitch.setText(f"{math.degrees(pitch):.2f}°")
            if hasattr(self, 'lbl_yaw'):
                self.lbl_yaw.setText(f"{math.degrees(yaw):.2f}°")
            self.yaw = yaw
        except Exception as e:
            print(f"Error updating attitude: {e}")

    def update_hud(self, airspeed, groundspeed, alt, heading):
        self.airspeed = airspeed
        self.groundspeed = groundspeed
        self.alt = alt
        self.hud.update_vfr(math.degrees(self.yaw), airspeed, groundspeed, alt)

    def update_gps(self, fix_type, satellites, hdop, vdop, lat, lon):
        fix_map = {0:"No GPS", 1:"No Fix", 2:"2D", 3:"3D", 4:"DGPS", 5:"RTK Float", 6:"RTK Fixed"}
        self.lbl_gps_fix.setText(fix_map.get(fix_type, "Unknown"))
        self.lbl_gps_sats.setText(str(satellites))
        self.lbl_gps_hdop.setText(f"{hdop:.2f}")
        self.lbl_gps_vdop.setText(f"{vdop:.2f}")
        self.lbl_gps_lat.setText(f"{lat:.6f}")
        self.lbl_gps_lon.setText(f"{lon:.6f}")
        # Update HUD with GPS info
        self.hud.update_gps(fix_type, satellites)
        # Update map with position
        if hasattr(self, 'map_widget') and self.map_widget:
            self.map_widget.update_uav_position(lat, lon)

    def update_status(self, voltage, current, remaining):
        self.lbl_status_volt.setText(f"{voltage:.2f} V")
        self.lbl_status_curr.setText(f"{current:.2f} A")
        self.lbl_status_rem.setText(f"{remaining}%" if remaining >= 0 else "N/A")
        # Update HUD with battery level
        self.hud.update_battery(remaining)

    def update_position(self, lat, lon, alt):
        """Update UAV position on map"""
        if hasattr(self, 'map_widget') and self.map_widget and (lat != 0 or lon != 0):
            # Calculate heading from yaw
            heading_deg = math.degrees(self.yaw) if hasattr(self, 'yaw') else 0
            self.map_widget.update_uav_position(lat, lon, heading_deg)
    
    def set_home_position(self, lat, lon):
        """Set home position on map"""
        if hasattr(self, 'map_widget') and self.map_widget:
            self.map_widget.set_home_position(lat, lon)
    
    def get_current_position(self):
        """Get current UAV position from map"""
        if hasattr(self, 'map_widget') and self.map_widget:
            return self.map_widget.overlays.overlays['uav']['data']
        return None
    
    def get_home_position(self):
        """Get home position from map"""
        if hasattr(self, 'map_widget') and self.map_widget:
            return self.map_widget.overlays.overlays['home']['data']
        return None
    
    def clear_flight_path(self):
        """Clear flight path on map"""
        if hasattr(self, 'map_widget') and self.map_widget:
            self.map_widget.clear_flight_path()
    
    def closeEvent(self, event):
        """Proper cleanup on application close"""
        try:
            # Stop MAVLink worker
            if hasattr(self, 'mavlink_worker') and self.mavlink_worker:
                self.mavlink_worker.stop()
                
            # Stop controller timer
            if hasattr(self, 'controller') and self.controller and hasattr(self.controller, 'timer'):
                self.controller.timer.stop()
                
            # Cleanup map widget
            if hasattr(self, 'map_widget') and self.map_widget:
                self.map_widget.closeEvent(event)
                
            # Stop performance monitoring
            if hasattr(self, 'performance_monitor') and self.performance_monitor:
                self.performance_monitor.stop()
                
        except Exception as e:
            print(f"Error during cleanup: {e}")
            
        event.accept()
