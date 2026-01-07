"""
ASRA GCS - Connection Sidebar Widget
Centralized connection panel for all drones
Matches React UI left sidebar
"""

import serial.tools.list_ports
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QGroupBox


class ConnectionSidebar(QWidget):
    """
    Left sidebar with connection controls for all drones
    """
    
    connect_requested = QtCore.pyqtSignal(str, str, int)  # drone_id, port, baud
    disconnect_requested = QtCore.pyqtSignal(str)  # drone_id
    
    def __init__(self, drone_manager, parent=None):
        super().__init__(parent)
        self.drone_manager = drone_manager
        self.setFixedWidth(250)
        self._setup_ui()
        
    def _setup_ui(self):
        """Create sidebar UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Sidebar styling
        self.setStyleSheet("""
            ConnectionSidebar {
                background-color: #0a0a0a;
                border-right: 1px solid #2a2a2a;
            }
            QGroupBox {
                background-color: #1a1a1a;
                border: 1px solid #2a2a2a;
                border-radius: 6px;
                padding: 12px;
                margin-top: 8px;
                font-weight: bold;
                color: #00d4ff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 6px;
            }
            QLabel {
                color: #9ca3af;
                font-size: 9pt;
            }
            QComboBox {
                background-color: #0a0a0a;
                border: 1px solid #2a2a2a;
                border-radius: 4px;
                padding: 6px;
                color: white;
                font-size: 9pt;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #9ca3af;
                margin-right: 6px;
            }
            QPushButton {
                background-color: #0078d4;
                border: none;
                border-radius: 4px;
                padding: 8px;
                color: white;
                font-weight: bold;
                font-size: 9pt;
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
        """)
        
        # Title
        title = QLabel("CONNECTION")
        title.setStyleSheet("""
            color: white;
            font-size: 11pt;
            font-weight: bold;
            padding-bottom: 8px;
        """)
        layout.addWidget(title)
        
        # Drone 1 connection
        self.drone1_group = self._create_drone_connection_group("Drone 1", "drone_1", "#00d4ff")
        layout.addWidget(self.drone1_group)
        
        # Drone 2 connection
        self.drone2_group = self._create_drone_connection_group("Drone 2", "drone_2", "#a78bfa")
        layout.addWidget(self.drone2_group)
        
        # System status
        status_group = QGroupBox("System Status")
        status_layout = QVBoxLayout(status_group)
        status_layout.setSpacing(6)
        
        self.lbl_status = QLabel("● Ready")
        self.lbl_status.setStyleSheet("color: #00ff88; font-size: 10pt; font-weight: bold;")
        status_layout.addWidget(self.lbl_status)
        
        self.lbl_connected = QLabel("Connected: 0/2")
        self.lbl_connected.setStyleSheet("color: #9ca3af; font-size: 9pt;")
        status_layout.addWidget(self.lbl_connected)
        
        layout.addWidget(status_group)
        
        layout.addStretch()
        
    def _create_drone_connection_group(self, name, drone_id, color):
        """Create connection controls for one drone"""
        group = QGroupBox(name)
        group.setStyleSheet(f"""
            QGroupBox {{
                background-color: #1a1a1a;
                border: 1px solid {color}40;
                border-radius: 6px;
                padding: 12px;
                margin-top: 8px;
                font-weight: bold;
                color: {color};
            }}
        """)
        
        layout = QVBoxLayout(group)
        layout.setSpacing(8)
        
        # Port selection
        port_layout = QVBoxLayout()
        port_layout.setSpacing(4)
        
        lbl_port = QLabel("Port:")
        combo_port = QComboBox()
        combo_port.setObjectName(f"{drone_id}_port")
        self._refresh_ports(combo_port)
        
        btn_refresh = QPushButton("↻")
        btn_refresh.setFixedWidth(32)
        btn_refresh.clicked.connect(lambda: self._refresh_ports(combo_port))
        
        port_row = QHBoxLayout()
        port_row.addWidget(combo_port, 1)
        port_row.addWidget(btn_refresh)
        
        port_layout.addWidget(lbl_port)
        port_layout.addLayout(port_row)
        
        layout.addLayout(port_layout)
        
        # Baud selection
        baud_layout = QVBoxLayout()
        baud_layout.setSpacing(4)
        
        lbl_baud = QLabel("Baud:")
        combo_baud = QComboBox()
        combo_baud.setObjectName(f"{drone_id}_baud")
        combo_baud.addItems(["57600", "115200", "230400"])
        
        baud_layout.addWidget(lbl_baud)
        baud_layout.addWidget(combo_baud)
        
        layout.addLayout(baud_layout)
        
        # Connect/Disconnect buttons
        btn_connect = QPushButton("Connect")
        btn_connect.setObjectName(f"{drone_id}_connect")
        btn_connect.setStyleSheet("""
            QPushButton {
                background-color: #00aa00;
            }
            QPushButton:hover {
                background-color: #00cc00;
            }
            QPushButton:pressed {
                background-color: #008800;
            }
        """)
        btn_connect.clicked.connect(
            lambda: self._on_connect(drone_id, combo_port.currentText(), int(combo_baud.currentText()))
        )
        
        btn_disconnect = QPushButton("Disconnect")
        btn_disconnect.setObjectName(f"{drone_id}_disconnect")
        btn_disconnect.setEnabled(False)
        btn_disconnect.setStyleSheet("""
            QPushButton {
                background-color: #aa0000;
            }
            QPushButton:hover {
                background-color: #cc0000;
            }
            QPushButton:pressed {
                background-color: #880000;
            }
        """)
        btn_disconnect.clicked.connect(lambda: self._on_disconnect(drone_id))
        
        layout.addWidget(btn_connect)
        layout.addWidget(btn_disconnect)
        
        # Status indicator
        status = QLabel("● Disconnected")
        status.setObjectName(f"{drone_id}_status")
        status.setStyleSheet("color: #ff3333; font-size: 9pt;")
        layout.addWidget(status)
        
        return group
    
    def _refresh_ports(self, combo):
        """Refresh COM ports in dropdown"""
        ports = [f"{p.device} - {p.description}" for p in serial.tools.list_ports.comports()]
        combo.clear()
        combo.addItems(ports if ports else ["No ports detected"])
    
    def _on_connect(self, drone_id, port_text, baud):
        """Handle connect button"""
        if "No ports" in port_text:
            return
        
        port = port_text.split(" - ")[0]
        self.connect_requested.emit(drone_id, port, baud)
        
        # Update UI
        connect_btn = self.findChild(QPushButton, f"{drone_id}_connect")
        disconnect_btn = self.findChild(QPushButton, f"{drone_id}_disconnect")
        status_lbl = self.findChild(QLabel, f"{drone_id}_status")
        
        if connect_btn:
            connect_btn.setEnabled(False)
        if disconnect_btn:
            disconnect_btn.setEnabled(True)
        if status_lbl:
            status_lbl.setText("● Connecting...")
            status_lbl.setStyleSheet("color: #ffa500; font-size: 9pt;")
    
    def _on_disconnect(self, drone_id):
        """Handle disconnect button"""
        self.disconnect_requested.emit(drone_id)
        
        # Update UI
        connect_btn = self.findChild(QPushButton, f"{drone_id}_connect")
        disconnect_btn = self.findChild(QPushButton, f"{drone_id}_disconnect")
        status_lbl = self.findChild(QLabel, f"{drone_id}_status")
        
        if connect_btn:
            connect_btn.setEnabled(True)
        if disconnect_btn:
            disconnect_btn.setEnabled(False)
        if status_lbl:
            status_lbl.setText("● Disconnected")
            status_lbl.setStyleSheet("color: #ff3333; font-size: 9pt;")
    
    def update_connection_status(self, drone_id, connected):
        """Update connection status display"""
        status_lbl = self.findChild(QLabel, f"{drone_id}_status")
        if status_lbl:
            if connected:
                status_lbl.setText("● Connected")
                status_lbl.setStyleSheet("color: #00ff88; font-size: 9pt;")
            else:
                status_lbl.setText("● Disconnected")
                status_lbl.setStyleSheet("color: #ff3333; font-size: 9pt;")
        
        # Update system status
        drone1_connected = self.drone_manager.get_drone("drone_1").connected if self.drone_manager.get_drone("drone_1") else False
        drone2_connected = self.drone_manager.get_drone("drone_2").connected if self.drone_manager.get_drone("drone_2") else False
        
        count = (1 if drone1_connected else 0) + (1 if drone2_connected else 0)
        self.lbl_connected.setText(f"Connected: {count}/2")
        
        if count == 2:
            self.lbl_status.setText("● All Systems Active")
            self.lbl_status.setStyleSheet("color: #00ff88; font-size: 10pt; font-weight: bold;")
        elif count == 1:
            self.lbl_status.setText("● Partial Connection")
            self.lbl_status.setStyleSheet("color: #ffa500; font-size: 10pt; font-weight: bold;")
        else:
            self.lbl_status.setText("● Ready")
            self.lbl_status.setStyleSheet("color: #9ca3af; font-size: 10pt; font-weight: bold;")
