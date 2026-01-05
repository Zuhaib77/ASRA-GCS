"""
ASRA GCS - Enhanced Drone Panel Widget v2
With connection controls and exception handling
"""

import math
import serial.tools.list_ports
from PyQt5 import QtCore, QtGui, QtWidgets
from hud_widget_reference_style import ReferenceStyleHUDWidget


class DronePanelWidget(QtWidgets.QWidget):
    """Individual drone panel with connection controls"""
    
    def __init__(self, drone_id, drone_manager, parent=None):
        super().__init__(parent)
        self.drone_id = drone_id
        self.drone_manager = drone_manager
        
        drone = drone_manager.get_drone(drone_id)
        self.drone_color = drone.color if drone else "#FF0000"
        self.drone_name = drone.name if drone else "Unknown"
        
        self._setup_ui()
        
        # Connect signals
        self.drone_manager.drone_telemetry_updated.connect(self._on_telemetry_update)
        self.drone_manager.drone_connected.connect(self._on_connection_changed)
        self.drone_manager.drone_disconnected.connect(self._on_connection_changed)
        
    def _setup_ui(self):
        """Create UI"""
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
                subcontrolorigin: margin;
                subcontrol-position: top center;
                padding: 0 8px;
                color: {self.drone_color};
            }}
            QPushButton {{
                background-color: #0078d4;
                border: 1px solid #005a9e;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
                color: white;
            }}
            QPushButton:hover {{ background-color: #1084d8; }}
            QPushButton:pressed {{ background-color: #005a9e; }}
            QPushButton:disabled {{ background-color: #404040; color: #808080; }}
            QComboBox {{
                background-color: #404040;
                border: 1px solid #555555;
                padding: 4px 8px;
                border-radius: 4px;
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
        
        main_layout = QtWidgets.QVBoxLayout(self)
        
        # Header
        header = QtWidgets.QLabel(f"<b style='color: {self.drone_color}'>● {self.drone_name}</b>")
        header.setStyleSheet("font-size: 11pt; padding: 5px;")
        main_layout.addWidget(header)
        
        # Content split: HUD | Panels
        content_layout = QtWidgets.QHBoxLayout()
        
        # Left: HUD
        self.hud = ReferenceStyleHUDWidget(self)
        self.hud.setFixedSize(400, 350)
        content_layout.addWidget(self.hud)
        
        # Right: Telemetry + Controls
        right_panel = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_panel)
        
        # Connection panel
        conn_box = self._create_connection_panel()
        right_layout.addWidget(conn_box)
        
        # Telemetry panels
        right_layout.addWidget(self._create_telemetry_groupbox("Attitude", [
            ("Roll", "lbl_roll"), ("Pitch", "lbl_pitch"), ("Yaw", "lbl_yaw"), ("Mode", "lbl_mode")
        ]))
        
        right_layout.addWidget(self._create_telemetry_groupbox("GPS", [
            ("Fix", "lbl_gps_fix"), ("Sats", "lbl_gps_sats"), 
            ("Lat", "lbl_gps_lat"), ("Lon", "lbl_gps_lon")
        ]))
        
        right_layout.addWidget(self._create_telemetry_groupbox("Battery", [
            ("Voltage", "lbl_status_volt"), ("Current", "lbl_status_curr"), ("Remaining", "lbl_status_rem")
        ]))
        
        # Control actions
        right_layout.addWidget(self._create_actions_panel())
        right_layout.addStretch()
        
        content_layout.addWidget(right_panel)
        main_layout.addLayout(content_layout)
        
        # Messages
        msg_box = QtWidgets.QGroupBox("Messages")
        msg_layout = QtWidgets.QVBoxLayout(msg_box)
        self.message_area = QtWidgets.QTextEdit()
        self.message_area.setReadOnly(True)
        self.message_area.setMaximumHeight(100)
        msg_layout.addWidget(self.message_area)
        main_layout.addWidget(msg_box)
        
    def _create_connection_panel(self):
        """Create connection controls"""
        box = QtWidgets.QGroupBox("Connection")
        layout = QtWidgets.QGridLayout(box)
        
        self.combo_port = QtWidgets.QComboBox()
        self.combo_baud = QtWidgets.QComboBox()
        self.combo_baud.addItems(["57600", "115200", "230400"])
        
        self.btn_refresh = QtWidgets.QPushButton("↻")
        self.btn_refresh.setMaximumWidth(30)
        self.btn_refresh.clicked.connect(self._refresh_ports)
        
        self.btn_connect = QtWidgets.QPushButton("Connect")
        self.btn_connect.clicked.connect(self._on_connect)
        self.btn_connect.setStyleSheet("background-color: #00aa00;")
        
        self.btn_disconnect = QtWidgets.QPushButton("Disconnect")
        self.btn_disconnect.clicked.connect(self._on_disconnect)
        self.btn_disconnect.setEnabled(False)
        self.btn_disconnect.setStyleSheet("background-color: #aa0000;")
        
        layout.addWidget(QtWidgets.QLabel("Port:"), 0, 0)
        layout.addWidget(self.combo_port, 0, 1)
        layout.addWidget(self.btn_refresh, 0, 2)
        layout.addWidget(QtWidgets.QLabel("Baud:"), 1, 0)
        layout.addWidget(self.combo_baud, 1, 1, 1, 2)
        layout.addWidget(self.btn_connect, 2, 0, 1, 2)
        layout.addWidget(self.btn_disconnect, 2, 2)
        
        self._refresh_ports()
        return box
    
    def _create_telemetry_groupbox(self, title, labels):
        """Create telemetry display"""
        box = QtWidgets.QGroupBox(title)
        layout = QtWidgets.QGridLayout(box)
        for i, (text, name) in enumerate(labels):
            lbl = QtWidgets.QLabel(f"{text}:")
            val = QtWidgets.QLabel("N/A")
            setattr(self, name, val)
            layout.addWidget(lbl, i, 0)
            layout.addWidget(val, i, 1)
        return box
    
    def _create_actions_panel(self):
        """Create control actions"""
        box = QtWidgets.QGroupBox("Vehicle Control")
        layout = QtWidgets.QGridLayout(box)
        
        self.btn_arm = QtWidgets.QPushButton("Arm/Disarm")
        self.btn_arm.clicked.connect(self._on_arm_disarm)
        
        self.combo_modes = QtWidgets.QComboBox()
        self.combo_modes.addItems(["Stabilize", "Alt Hold", "Loiter", "Auto", "Guided", "RTL", "Land"])
        
        self.btn_set_mode = QtWidgets.QPushButton("Set Mode")
        self.btn_set_mode.clicked.connect(self._on_set_mode)
        
        layout.addWidget(self.btn_arm, 0, 0, 1, 2)
        layout.addWidget(self.combo_modes, 1, 0)
        layout.addWidget(self.btn_set_mode, 1, 1)
        
        return box
    
    # Connection handlers
    def _refresh_ports(self):
        """Refresh COM ports"""
        ports = [f"{p.device} - {p.description}" for p in serial.tools.list_ports.comports()]
        self.combo_port.clear()
        self.combo_port.addItems(ports if ports else ["No ports detected"])
    
    def _on_connect(self):
        """Connect to drone"""
        port = self.combo_port.currentText()
        if "No ports" in port:
            QtWidgets.QMessageBox.warning(self, "No Ports", "No COM ports detected")
            return
        
        baud = int(self.combo_baud.currentText())
        drone = self.drone_manager.get_drone(self.drone_id)
        if drone:
            drone.port = port.split(" - ")[0]
            drone.baud = baud
            drone.worker.configure(drone.port, baud)
        
        self.drone_manager.connect_drone(self.drone_id)
        self.append_message(f"Connecting to {port} @ {baud}...")
        
        self.btn_connect.setEnabled(False)
        self.btn_disconnect.setEnabled(True)
    
    def _on_disconnect(self):
        """Disconnect from drone"""
        self.drone_manager.disconnect_drone(self.drone_id)
        self.append_message("Disconnected")
        self.btn_connect.setEnabled(True)
        self.btn_disconnect.setEnabled(False)
    
    def _check_connection(self):
        """Check if connected"""
        drone = self.drone_manager.get_drone(self.drone_id)
        if not drone or not drone.connected:
            QtWidgets.QMessageBox.warning(
                self, "Not Connected",
                f"{self.drone_name} is not connected!"
            )
            return False
        return True
    
    # Command handlers
    def _on_arm_disarm(self):
        if not self._check_connection():
            return
        self.drone_manager.send_command(self.drone_id, 'arm_disarm')
        self.append_message("Arm/Disarm command sent")
    
    def _on_set_mode(self):
        if not self._check_connection():
            return
        mode = self.combo_modes.currentText()
        modes = {"Stabilize": 0, "Alt Hold": 2, "Loiter": 5, "RTL": 6, "Land": 9, "Auto": 3, "Guided": 4}
        if mode in modes:
            self.drone_manager.send_command(self.drone_id, 'set_mode', modes[mode])
            self.append_message(f"Setting mode to {mode}...")
    
    # Telemetry updates
    def _on_telemetry_update(self, drone_id, msg_type, data):
        if drone_id != self.drone_id:
            return
        
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
        self.hud.update_attitude(data.get('roll', 0), data.get('pitch', 0), data.get('yaw', 0))
        self.lbl_roll.setText(f"{math.degrees(data.get('roll', 0)):.1f}°")
        self.lbl_pitch.setText(f"{math.degrees(data.get('pitch', 0)):.1f}°")
        self.lbl_yaw.setText(f"{math.degrees(data.get('yaw', 0)):.1f}°")
    
    def _update_vfr(self, data):
        self.hud.update_vfr(data.get('heading', 0), data.get('airspeed', 0), 
                           data.get('groundspeed', 0), data.get('alt', 0))
    
    def _update_gps(self, data):
        fix_map = {0: "No GPS", 1: "No Fix", 2: "2D", 3: "3D", 4: "DGPS", 5: "RTK"}
        self.lbl_gps_fix.setText(fix_map.get(data.get('fix_type', 0), "Unknown"))
        self.lbl_gps_sats.setText(str(data.get('satellites', 0)))
        self.lbl_gps_lat.setText(f"{data.get('lat', 0):.6f}")
        self.lbl_gps_lon.setText(f"{data.get('lon', 0):.6f}")
        self.hud.update_gps(data.get('fix_type', 0), data.get('satellites', 0))
    
    def _update_status(self, data):
        self.lbl_status_volt.setText(f"{data.get('voltage', 0):.1f}V")
        self.lbl_status_curr.setText(f"{data.get('current', 0):.1f}A")
        rem = data.get('remaining', -1)
        self.lbl_status_rem.setText(f"{rem}%" if rem >= 0 else "N/A")
        self.hud.update_battery(rem)
    
    def _update_flight_mode(self, mode):
        self.lbl_mode.setText(mode)
        self.hud.update_flight_mode(mode)
    
    def _on_connection_changed(self, drone_id):
        if drone_id != self.drone_id:
            return
        drone = self.drone_manager.get_drone(drone_id)
        if drone:
            self.hud.update_connection_status(drone.connected)
            self.hud.update_armed_status(drone.armed)
    
    def append_message(self, msg):
        self.message_area.append(msg)
