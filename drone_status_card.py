"""
ASRA GCS - Drone Status Card Widget (Refined)
Properly measured, aligned, no overlapping, text fits boxes
"""

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton


class DroneStatusCard(QWidget):
    """
    Compact drone status card - refined with proper sizing
    """
    
    arm_clicked = QtCore.pyqtSignal(str)
    
    def __init__(self, drone_id, drone_manager, drone_color="#00d4ff", parent=None):
        super().__init__(parent)
        self.drone_id = drone_id
        self.drone_manager = drone_manager
        self.drone_color = drone_color
        
        drone = drone_manager.get_drone(drone_id)
        self.drone_name = drone.name if drone else "Unknown"
        
        # Set fixed/minimum size for predictable layout
        self.setMinimumWidth(260)
        self.setMaximumWidth(320)
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Create UI with precise measurements"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        self.setStyleSheet(f"""
            DroneStatusCard {{
                background-color: #1a1a1a;
                border: 2px solid {self.drone_color}40;
                border-radius: 6px;
            }}
        """)
        
        # Header: Name + Armed badge (fixed height: 24px)
        header = QHBoxLayout()
        header.setSpacing(8)
        header.setContentsMargins(0, 0, 0, 0)
        
        # Left: Color dot + Name
        name_layout = QHBoxLayout()
        name_layout.setSpacing(6)
        name_layout.setContentsMargins(0, 0, 0, 0)
        
        color_dot = QLabel()
        color_dot.setFixedSize(10, 10)
        color_dot.setStyleSheet(f"background-color: {self.drone_color}; border-radius: 5px;")
        
        self.lbl_name = QLabel(self.drone_name)
        self.lbl_name.setStyleSheet("color: white; font-size: 10pt; font-weight: bold;")
        self.lbl_name.setFixedHeight(20)
        
        name_layout.addWidget(color_dot)
        name_layout.addWidget(self.lbl_name)
        name_layout.addStretch()
        
        # Right: Armed badge
        self.lbl_armed = QLabel("DISARMED")
        self.lbl_armed.setFixedHeight(20)
        self.lbl_armed.setAlignment(Qt.AlignCenter)
        self.lbl_armed.setStyleSheet("""
            background-color: #404040;
            color: #9ca3af;
            border: 1px solid #555555;
            border-radius: 3px;
            padding: 2px 6px;
            font-size: 8pt;
            font-weight: bold;
            font-family: 'Consolas', monospace;
        """)
        
        header.addLayout(name_layout, 1)
        header.addWidget(self.lbl_armed)
        layout.addLayout(header)
        
        # Quick stats (4 columns, fixed height: 50px)
        stats = QGridLayout()
        stats.setSpacing(4)
        stats.setContentsMargins(0, 0, 0, 0)
        
        self.stat_battery = self._create_stat("⚡", "100%", "#00ff88")
        self.stat_signal = self._create_stat("📶", "95%", "#00ff88")
        self.stat_satellites = self._create_stat("🛰", "12", "#00d4ff")
        self.stat_distance = self._create_stat("📍", "0m", "#ffa500")
        
        stats.addWidget(self.stat_battery, 0, 0)
        stats.addWidget(self.stat_signal, 0, 1)
        stats.addWidget(self.stat_satellites, 0, 2)
        stats.addWidget(self.stat_distance, 0, 3)
        
        layout.addLayout(stats)
        
        # Flight data (3 columns, fixed height: 50px)
        flight = QGridLayout()
        flight.setSpacing(4)
        flight.setContentsMargins(0, 0, 0, 0)
        
        self.flight_alt = self._create_flight_widget("ALT", "0m")
        self.flight_spd = self._create_flight_widget("SPD", "0.0")
        self.flight_hdg = self._create_flight_widget("HDG", "0°")
        
        flight.addWidget(self.flight_alt, 0, 0)
        flight.addWidget(self.flight_spd, 0, 1)
        flight.addWidget(self.flight_hdg, 0, 2)
        
        layout.addLayout(flight)
        
        # Bottom: Mode + Arm button (fixed height: 32px)
        bottom = QHBoxLayout()
        bottom.setSpacing(6)
        bottom.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_mode = QLabel("STABILIZE")
        self.lbl_mode.setFixedHeight(28)
        self.lbl_mode.setAlignment(Qt.AlignCenter)
        self.lbl_mode.setStyleSheet(f"""
            background-color: {self.drone_color}30;
            color: {self.drone_color};
            border: 1px solid {self.drone_color}80;
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 9pt;
            font-weight: bold;
            font-family: 'Consolas', monospace;
        """)
        
        self.btn_arm = QPushButton("⚡")
        self.btn_arm.setFixedSize(28, 28)
        self.btn_arm.clicked.connect(lambda: self.arm_clicked.emit(self.drone_id))
        self.btn_arm.setStyleSheet("""
            QPushButton {
                background-color: #00ff8830;
                color: #00ff88;
                border: 1px solid #00ff8880;
                border-radius: 4px;
                font-size: 12pt;
            }
            QPushButton:hover { background-color: #00ff8850; }
            QPushButton:pressed { background-color: #00ff8820; }
        """)
        
        bottom.addWidget(self.lbl_mode, 1)
        bottom.addWidget(self.btn_arm)
        
        layout.addLayout(bottom)
        layout.addStretch()
        
    def _create_stat(self, icon, value, color):
        """Create stat widget with fixed size"""
        widget = QWidget()
        widget.setFixedHeight(48)
        widget.setStyleSheet("background-color: #0a0a0a; border-radius: 3px;")
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(2, 4, 2, 4)
        layout.setSpacing(2)
        
        lbl_icon = QLabel(icon)
        lbl_icon.setAlignment(Qt.AlignCenter)
        lbl_icon.setFixedHeight(16)
        lbl_icon.setStyleSheet(f"font-size: 11pt; color: {color};")
        
        lbl_value = QLabel(value)
        lbl_value.setObjectName("value")
        lbl_value.setAlignment(Qt.AlignCenter)
        lbl_value.setFixedHeight(18)
        lbl_value.setStyleSheet(f"""
            font-size: 8pt;
            font-weight: bold;
            font-family: 'Consolas', monospace;
            color: {color};
        """)
        
        layout.addWidget(lbl_icon)
        layout.addWidget(lbl_value)
        layout.addStretch()
        
        return widget
    
    def _create_flight_widget(self, label, value):
        """Create flight data widget with fixed size"""
        widget = QWidget()
        widget.setFixedHeight(48)
        widget.setStyleSheet("background-color: #0a0a0a; border-radius: 3px;")
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(2, 4, 2, 4)
        layout.setSpacing(2)
        
        lbl_label = QLabel(label)
        lbl_label.setAlignment(Qt.AlignCenter)
        lbl_label.setFixedHeight(14)
        lbl_label.setStyleSheet("""
            font-size: 7pt;
            color: #9ca3af;
            font-family: 'Consolas', monospace;
        """)
        
        lbl_value = QLabel(value)
        lbl_value.setObjectName("value")
        lbl_value.setAlignment(Qt.AlignCenter)
        lbl_value.setFixedHeight(20)
        lbl_value.setStyleSheet("""
            font-size: 10pt;
            font-weight: bold;
            color: white;
            font-family: 'Consolas', monospace;
        """)
        
        layout.addWidget(lbl_label)
        layout.addWidget(lbl_value)
        layout.addStretch()
        
        return widget
    
    def update_status(self, telemetry):
        """Update card with telemetry data"""
        # Armed status
        armed = telemetry.get('armed', False)
        if armed:
            self.lbl_armed.setText("ARMED")
            self.lbl_armed.setStyleSheet("""
                background-color: #00ff8830;
                color: #00ff88;
                border: 1px solid #00ff8880;
                border-radius: 3px;
                padding: 2px 6px;
                font-size: 8pt;
                font-weight: bold;
                font-family: 'Consolas', monospace;
            """)
            self.btn_arm.setStyleSheet("""
                QPushButton {
                    background-color: #ff333330;
                    color: #ff3333;
                    border: 1px solid #ff333380;
                    border-radius: 4px;
                    font-size: 12pt;
                }
                QPushButton:hover { background-color: #ff333350; }
            """)
        else:
            self.lbl_armed.setText("DISARMED")
            self.lbl_armed.setStyleSheet("""
                background-color: #404040;
                color: #9ca3af;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 2px 6px;
                font-size: 8pt;
                font-weight: bold;
                font-family: 'Consolas', monospace;
            """)
        
        # Update stats with proper elision
        battery = telemetry.get('battery_percent', 100)
        self._update_stat(self.stat_battery, f"{battery:.0f}%", self._get_battery_color(battery))
        
        rssi = telemetry.get('rssi', 0)
        self._update_stat(self.stat_signal, f"{rssi}%", self._get_signal_color(rssi))
        
        sats = telemetry.get('satellites', 0)
        self._update_stat(self.stat_satellites, str(sats), "#00d4ff")
        
        distance = telemetry.get('distance_to_home', 0)
        if distance > 999:
            dist_text = f"{distance/1000:.1f}km"
        else:
            dist_text = f"{distance:.0f}m"
        self._update_stat(self.stat_distance, dist_text, "#ffa500")
        
        # Update flight data
        alt = telemetry.get('altitude_agl', 0)
        self._update_flight(self.flight_alt, f"{alt:.0f}m" if alt < 1000 else f"{alt/1000:.1f}km")
        
        spd = telemetry.get('ground_speed', 0)
        self._update_flight(self.flight_spd, f"{spd:.1f}")
        
        hdg = telemetry.get('heading', 0)
        self._update_flight(self.flight_hdg, f"{hdg:.0f}°")
        
        # Mode (elide if too long)
        mode = telemetry.get('flight_mode', 'UNKNOWN')
        if len(mode) > 10:
            mode = mode[:10]
        self.lbl_mode.setText(mode)
    
    def _update_stat(self, widget, value, color):
        """Update stat widget value"""
        lbl = widget.findChild(QLabel, "value")
        if lbl:
            lbl.setText(value)
            lbl.setStyleSheet(f"""
                font-size: 8pt;
                font-weight: bold;
                font-family: 'Consolas', monospace;
                color: {color};
            """)
    
    def _update_flight(self, widget, value):
        """Update flight widget value"""
        lbl = widget.findChild(QLabel, "value")
        if lbl:
            lbl.setText(value)
    
    def _get_battery_color(self, percent):
        return "#00ff88" if percent > 50 else "#ffa500" if percent > 25 else "#ff3333"
    
    def _get_signal_color(self, rssi):
        return "#00ff88" if rssi > 70 else "#ffa500" if rssi > 40 else "#ff3333"
