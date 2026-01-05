"""
ASRA GCS - Individual Drone Panel Widget
UI panel for controlling and monitoring a single drone
Used in multi-drone tabbed or grid layout
"""

import math
from PyQt5 import QtCore, QtGui, QtWidgets
from hud_widget_reference_style import ReferenceStyleHUDWidget


class DronePanelWidget(QtWidgets.QWidget):
    """
    Individual drone control panel
    Contains HUD, telemetry displays, and control buttons for one drone
    """
    
    def __init__(self, drone_id, drone_manager, parent=None):
        super().__init__(parent)
        self.drone_id = drone_id
        self.drone_manager = drone_manager
        
        # Get drone info
        drone = drone_manager.get_drone(drone_id)
        self.drone_color = drone.color if drone else "#FF0000"
        self.drone_name = drone.name if drone else "Unknown"
        
        # Setup UI
        self._setup_ui()
        
        # Connect to drone manager signals
        self.drone_manager.drone_telemetry_updated.connect(self._on_telemetry_update)
        self.drone_manager.drone_connected.connect(self._on_connection_changed)
        self.drone_manager.drone_disconnected.connect(self._on_connection_changed)
        
    def _setup_ui(self):
        """Create UI layout"""
        # Apply color-coded theme
        self.setStyleSheet(f"""
            QWidget {{
                background-color: #2a2a2a;
                color: #ffffff;
                font-family: Arial, sans-serif;
                font-size: 9pt;
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {self.drone_color};
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: #333333;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 8px;
                color: {self.drone_color};
            }}
            QPushButton {{
                background-color: #0078d4;
                border: 1px solid #005a9e;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                color: white;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: #1084d8;
            }}
            QPushButton:pressed {{
                background-color: #005a9e;
            }}
            QPushButton:disabled {{
                background-color: #404040;
                color: #808080;
            }}
            QComboBox {{
                background-color: #404040;
                border: 1px solid #555555;
                padding: 6px 12px;
                border-radius: 4px;
                min-width: 100px;
            }}
            QTextEdit {{
                background-color: #1a1a1a;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 8px;
                font-family: Consolas, monospace;
                font-size: 9pt;
            }}
        """)
        
        # Main layout
        main_layout = QtWidgets.QHBoxLayout(self)
        
        # Left: HUD
        self.hud = ReferenceStyleHUDWidget(self)
        self.hud.setFixedSize(480, 400)
        main_layout.addWidget(self.hud)
        
        # Right: Telemetry and controls
        right_panel = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_panel)
        
        # Drone info header
        info_label = QtWidgets.QLabel(f"<b style='color: {self.drone_color}'>● {self.drone_name}</b>")
        info_label.setStyleSheet("font-size: 12pt; padding: 5px;")
        right_layout.addWidget(info_label)
        
        # Telemetry panels
        attitude_box = self._create_telemetry_groupbox("Attitude", [
            ("Roll", "lbl_roll"),
            ("Pitch", "lbl_pitch"),
            ("Yaw", "lbl_yaw"),
            ("Mode", "lbl_mode")
        ])
        
        gps_box = self._create_telemetry_groupbox("GPS", [
            ("Fix Type", "lbl_gps_fix"),
            ("Satellites", "lbl_gps_sats"),
            ("HDOP", "lbl_gps_hdop"),
            ("VDOP", "lbl_gps_vdop"),
            ("Latitude", "lbl_gps_lat"),
            ("Longitude", "lbl_gps_lon")
        ])
        
        status_box = self._create_telemetry_groupbox("System Status", [
            ("Voltage", "lbl_status_volt"),
            ("Current", "lbl_status_curr"),
            ("Battery", "lbl_status_rem")
        ])
        
        actions_box = self._create_actions_groupbox()
        
        right_layout.addWidget(attitude_box)
        right_layout.addWidget(gps_box)
        right_layout.addWidget(status_box)
        right_layout.addWidget(actions_box)
        right_layout.addStretch()
        
        main_layout.addWidget(right_panel)
        
        # Messages panel (bottom)
        messages_box = QtWidgets.QGroupBox("Messages")
        messages_layout = QtWidgets.QVBoxLayout(messages_box)
        self.message_area = QtWidgets.QTextEdit()
        self.message_area.setReadOnly(True)
        self.message_area.setMaximumHeight(150)
        messages_layout.addWidget(self.message_area)
        
        # Add messages to main layout
        main_layout.addWidget(messages_box)
        
    def _create_telemetry_groupbox(self, title, labels):
        """Create telemetry display group box"""
        box = QtWidgets.QGroupBox(title)
        layout = QtWidgets.QGridLayout(box)
        
        for i, (text, name) in enumerate(labels):
            label = QtWidgets.QLabel(f"{text}:")
            value_label = QtWidgets.QLabel("N/A")
            setattr(self, name, value_label)
            layout.addWidget(label, i, 0)
            layout.addWidget(value_label, i, 1)
        
        return box
    
    def _create_actions_groupbox(self):
        """Create vehicle actions group box"""
        box = QtWidgets.QGroupBox("Vehicle Actions")
        layout = QtWidgets.QGridLayout(box)
        
        self.btn_arm_disarm = QtWidgets.QPushButton("Arm / Disarm")
        self.btn_arm_disarm.clicked.connect(self._on_arm_disarm)
        
        self.btn_force_arm = QtWidgets.QPushButton("Force Arm")
        self.btn_force_arm.clicked.connect(self._on_force_arm)
        
        self.combo_modes = QtWidgets.QComboBox()
        self.combo_modes.addItems(["Stabilize", "Alt Hold", "Loiter", "Auto", "Guided", "RTL", "Land"])
        
        self.btn_set_mode = QtWidgets.QPushButton("Set Mode")
        self.btn_set_mode.clicked.connect(self._on_set_mode)
        
        self.btn_mission_start = QtWidgets.QPushButton("Start Mission")
        self.btn_mission_start.clicked.connect(self._on_mission_start)
        
        self.btn_abort_land = QtWidgets.QPushButton("Abort Landing")
        self.btn_abort_land.clicked.connect(self._on_abort_land)
        
        layout.addWidget(self.btn_arm_disarm, 0, 0)
        layout.addWidget(self.btn_force_arm, 0, 1)
        layout.addWidget(self.combo_modes, 1, 0)
        layout.addWidget(self.btn_set_mode, 1, 1)
        layout.addWidget(self.btn_mission_start, 2, 0)
        layout.addWidget(self.btn_abort_land, 2, 1)
        
        return box
    
    def _on_telemetry_update(self, drone_id, msg_type, data):
        """Handle telemetry updates from drone manager"""
        # Only process updates for this drone
        if drone_id != self.drone_id:
            return
        
        # Route to appropriate update method
        if msg_type == "attitude":
            self._update_attitude(data)
        elif msg_type == "vfr_hud":
            self._update_vfr(data)
        elif msg_type == "gps":
            self._update_gps(data)
        elif msg_type == "sys_status":
            self._update_status(data)
        elif msg_type == "flight_mode":
            self._update_flight_mode(data)
        elif msg_type == "statustext":
            self.append_message(f"FCU: {data}")
    
    def _update_attitude(self, data):
        """Update attitude displays"""
        roll = data.get('roll', 0)
        pitch = data.get('pitch', 0)
        yaw = data.get('yaw', 0)
        
        self.hud.update_attitude(roll, pitch, yaw)
        self.lbl_roll.setText(f"{math.degrees(roll):.2f}°")
        self.lbl_pitch.setText(f"{math.degrees(pitch):.2f}°")
        self.lbl_yaw.setText(f"{math.degrees(yaw):.2f}°")
    
    def _update_vfr(self, data):
        """Update VFR HUD data"""
        airspeed = data.get('airspeed', 0)
        groundspeed = data.get('groundspeed', 0)
        alt = data.get('alt', 0)
        heading = data.get('heading', 0)
        
        self.hud.update_vfr(heading, airspeed, groundspeed, alt)
    
    def _update_gps(self, data):
        """Update GPS displays"""
        fix_map = {0: "No GPS", 1: "No Fix", 2: "2D", 3: "3D", 4: "DGPS", 5: "RTK Float", 6: "RTK Fixed"}
        
        fix_type = data.get('fix_type', 0)
        satellites = data.get('satellites', 0)
        hdop = data.get('hdop', 0)
        vdop = data.get('vdop', 0)
        lat = data.get('lat', 0)
        lon = data.get('lon', 0)
        
        self.lbl_gps_fix.setText(fix_map.get(fix_type, "Unknown"))
        self.lbl_gps_sats.setText(str(satellites))
        self.lbl_gps_hdop.setText(f"{hdop:.2f}")
        self.lbl_gps_vdop.setText(f"{vdop:.2f}")
        self.lbl_gps_lat.setText(f"{lat:.6f}")
        self.lbl_gps_lon.setText(f"{lon:.6f}")
        
        self.hud.update_gps(fix_type, satellites)
    
    def _update_status(self, data):
        """Update system status displays"""
        voltage = data.get('voltage', 0)
        current = data.get('current', 0)
        remaining = data.get('remaining', -1)
        
        self.lbl_status_volt.setText(f"{voltage:.2f} V")
        self.lbl_status_curr.setText(f"{current:.2f} A")
        self.lbl_status_rem.setText(f"{remaining}%" if remaining >= 0 else "N/A")
        
        self.hud.update_battery(remaining)
    
    def _update_flight_mode(self, mode):
        """Update flight mode display"""
        self.lbl_mode.setText(mode)
        self.hud.update_flight_mode(mode)
    
    def _on_connection_changed(self, drone_id):
        """Handle connection state changes"""
        if drone_id != self.drone_id:
            return
        
        drone = self.drone_manager.get_drone(drone_id)
        if drone:
            self.hud.update_connection_status(drone.connected)
            self.hud.update_armed_status(drone.armed)
    
    def append_message(self, msg):
        """Append message to messages area"""
        self.message_area.append(msg)
    
    # Command button handlers
    def _on_arm_disarm(self):
        """Handle arm/disarm button"""
        self.drone_manager.send_command(self.drone_id, 'arm_disarm')
        self.append_message("Sending Arm/Disarm command...")
    
    def _on_force_arm(self):
        """Handle force arm button"""
        reply = QtWidgets.QMessageBox.question(
            self, "Confirm Force Arm",
            "Are you sure you want to force arm? This bypasses safety checks.",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            self.drone_manager.send_command(self.drone_id, 'force_arm')
            self.append_message("Sending Force Arm command...")
    
    def _on_set_mode(self):
        """Handle set mode button"""
        mode_name = self.combo_modes.currentText()
        mode_mapping = {
            "Stabilize": 0, "Alt Hold": 2, "Loiter": 5,
            "RTL": 6, "Land": 9, "Auto": 3, "Guided": 4
        }
        mode_id = mode_mapping.get(mode_name)
        if mode_id is not None:
            self.drone_manager.send_command(self.drone_id, 'set_mode', mode_id)
            self.append_message(f"Setting mode to {mode_name}...")
    
    def _on_mission_start(self):
        """Handle mission start button"""
        reply = QtWidgets.QMessageBox.question(
            self, "Confirm Mission Start",
            "Are you sure you want to start the mission?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            self.drone_manager.send_command(self.drone_id, 'mission_start')
            self.append_message("Sending Mission Start command...")
    
    def _on_abort_land(self):
        """Handle abort landing button"""
        reply = QtWidgets.QMessageBox.question(
            self, "Confirm Abort Landing",
            "Are you sure you want to abort landing and RTL?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            self.drone_manager.send_command(self.drone_id, 'abort_land')
            self.append_message("Sending Abort Landing command...")
