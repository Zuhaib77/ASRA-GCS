"""
ASRA GCS - Drone Status Card Widget
Compact status display for drone in combined view
Matches React UI design
"""

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton


class DroneStatusCard(QWidget):
    """
    Compact drone status card showing key metrics
    Designed for combined view
    """
    
    arm_clicked = QtCore.pyqtSignal(str)  # drone_id
    
    def __init__(self, drone_id, drone_manager, drone_color="#00d4ff", parent=None):
        super().__init__(parent)
        self.drone_id = drone_id
        self.drone_manager = drone_manager
        self.drone_color = drone_color
        
        drone = drone_manager.get_drone(drone_id)
        self.drone_name = drone.name if drone else "Unknown"
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Create compact status card UI"""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Set card styling
        self.setStyleSheet(f"""
            DroneStatusCard {{
                background-color: #1a1a1a;
                border: 2px solid {self.drone_color}40;
                border-radius: 8px;
            }}
        """)
        
        # Header: Name + Status
        header = QHBoxLayout()
        
        # Color indicator + Name
        name_container = QHBoxLayout()
        name_container.setSpacing(8)
        
        color_dot = QLabel()
        color_dot.setFixedSize(12, 12)
        color_dot.setStyleSheet(f"""
            background-color: {self.drone_color};
            border-radius: 6px;
        """)
        
        self.lbl_name = QLabel(self.drone_name)
        self.lbl_name.setStyleSheet("color: white; font-size: 11pt; font-weight: bold;")
        
        name_container.addWidget(color_dot)
        name_container.addWidget(self.lbl_name)
        name_container.addStretch()
        
        # Armed status badge
        self.lbl_armed = QLabel("DISARMED")
        self.lbl_armed.setStyleSheet("""
            background-color: #404040;
            color: #9ca3af;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 9pt;
            font-weight: bold;
            font-family: 'Consolas', monospace;
        """)
        
        header.addLayout(name_container)
        header.addWidget(self.lbl_armed)
        layout.addLayout(header)
        
        # Quick stats grid (4 columns)
        stats_grid = QGridLayout()
        stats_grid.setSpacing(6)
        
        self.stat_battery = self._create_stat_widget("⚡", "100%", "#00ff88")
        self.stat_signal = self._create_stat_widget("📶", "95%", "#00ff88")
        self.stat_satellites = self._create_stat_widget("🛰", "12", "#00d4ff")
        self.stat_distance = self._create_stat_widget("📍", "0m", "#ffa500")
        
        stats_grid.addWidget(self.stat_battery, 0, 0)
        stats_grid.addWidget(self.stat_signal, 0, 1)
        stats_grid.addWidget(self.stat_satellites, 0, 2)
        stats_grid.addWidget(self.stat_distance, 0, 3)
        
        layout.addLayout(stats_grid)
        
        # Flight data (3 columns)
        flight_grid = QGridLayout()
        flight_grid.setSpacing(6)
        
        self.flight_alt = self._create_flight_data("ALT", "0m")
        self.flight_spd = self._create_flight_data("SPD", "0.0")
        self.flight_hdg = self._create_flight_data("HDG", "0°")
        
        flight_grid.addWidget(self.flight_alt, 0, 0)
        flight_grid.addWidget(self.flight_spd, 0, 1)
        flight_grid.addWidget(self.flight_hdg, 0, 2)
        
        layout.addLayout(flight_grid)
        
        # Mode + Arm button
        bottom = QHBoxLayout()
        bottom.setSpacing(6)
        
        self.lbl_mode = QLabel("STABILIZE")
        self.lbl_mode.setStyleSheet(f"""
            background-color: {self.drone_color}30;
            color: {self.drone_color};
            border: 1px solid {self.drone_color}80;
            border-radius: 4px;
            padding: 6px 12px;
            font-size: 10pt;
            font-weight: bold;
            font-family: 'Consolas', monospace;
        """)
        
        self.btn_arm = QPushButton("⚡")
        self.btn_arm.setFixedSize(32, 32)
        self.btn_arm.clicked.connect(lambda: self.arm_clicked.emit(self.drone_id))
        self.btn_arm.setStyleSheet("""
            QPushButton {
                background-color: #00ff8830;
                color: #00ff88;
                border: 1px solid #00ff8880;
                border-radius: 4px;
                font-size: 14pt;
            }
            QPushButton:hover {
                background-color: #00ff8850;
            }
            QPushButton:pressed {
                background-color: #00ff8820;
            }
        """)
        
        bottom.addWidget(self.lbl_mode, 1)
        bottom.addWidget(self.btn_arm)
        
        layout.addLayout(bottom)
        
    def _create_stat_widget(self, icon, value, color):
        """Create small stat widget"""
        widget = QWidget()
        widget.setStyleSheet("""
            background-color: #0a0a0a;
            border-radius: 4px;
            padding: 6px;
        """)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        
        lbl_icon = QLabel(icon)
        lbl_icon.setAlignment(Qt.AlignCenter)
        lbl_icon.setStyleSheet(f"font-size: 12pt; color: {color};")
        
        lbl_value = QLabel(value)
        lbl_value.setObjectName("value")
        lbl_value.setAlignment(Qt.AlignCenter)
        lbl_value.setStyleSheet(f"""
            font-size: 9pt;
            font-weight: bold;
            font-family: 'Consolas', monospace;
            color: {color};
        """)
        
        layout.addWidget(lbl_icon)
        layout.addWidget(lbl_value)
        
        return widget
    
    def _create_flight_data(self, label, value):
        """Create flight data display"""
        widget = QWidget()
        widget.setStyleSheet("""
            background-color: #0a0a0a;
            border-radius: 4px;
            padding: 6px;
        """)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        
        lbl_label = QLabel(label)
        lbl_label.setAlignment(Qt.AlignCenter)
        lbl_label.setStyleSheet("""
            font-size: 8pt;
            color: #9ca3af;
            font-family: 'Consolas', monospace;
        """)
        
        lbl_value = QLabel(value)
        lbl_value.setObjectName("value")
        lbl_value.setAlignment(Qt.AlignCenter)
        lbl_value.setStyleSheet("""
            font-size: 11pt;
            font-weight: bold;
            color: white;
            font-family: 'Consolas', monospace;
        """)
        
        layout.addWidget(lbl_label)
        layout.addWidget(lbl_value)
        
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
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 9pt;
                font-weight: bold;
                font-family: 'Consolas', monospace;
            """)
            self.btn_arm.setStyleSheet("""
                QPushButton {
                    background-color: #ff333330;
                    color: #ff3333;
                    border: 1px solid #ff333380;
                    border-radius: 4px;
                    font-size: 14pt;
                }
                QPushButton:hover {
                    background-color: #ff333350;
                }
            """)
        else:
            self.lbl_armed.setText("DISARMED")
            self.lbl_armed.setStyleSheet("""
                background-color: #404040;
                color: #9ca3af;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 9pt;
                font-weight: bold;
                font-family: 'Consolas', monospace;
            """)
        
        # Battery
        battery = telemetry.get('battery_percent', 100)
        battery_color = self._get_battery_color(battery)
        battery_widget = self.stat_battery.findChild(QLabel, "value")
        if battery_widget:
            battery_widget.setText(f"{battery:.0f}%")
            battery_widget.setStyleSheet(f"color: {battery_color}; font-size: 9pt; font-weight: bold; font-family: 'Consolas', monospace;")
        
        # Signal (RSSI)
        rssi = telemetry.get('rssi', 0)
        signal_color = self._get_signal_color(rssi)
        signal_widget = self.stat_signal.findChild(QLabel, "value")
        if signal_widget:
            signal_widget.setText(f"{rssi}%")
            signal_widget.setStyleSheet(f"color: {signal_color}; font-size: 9pt; font-weight: bold; font-family: 'Consolas', monospace;")
        
        # Satellites
        sats = telemetry.get('satellites', 0)
        sat_widget = self.stat_satellites.findChild(QLabel, "value")
        if sat_widget:
            sat_widget.setText(str(sats))
        
        # Distance to home
        distance = telemetry.get('distance_to_home', 0)
        dist_widget = self.stat_distance.findChild(QLabel, "value")
        if dist_widget:
            dist_widget.setText(f"{distance:.0f}m")
        
        # Flight data
        alt_widget = self.flight_alt.findChild(QLabel, "value")
        if alt_widget:
            alt_widget.setText(f"{telemetry.get('altitude_agl', 0):.0f}m")
        
        spd_widget = self.flight_spd.findChild(QLabel, "value")
        if spd_widget:
            spd_widget.setText(f"{telemetry.get('ground_speed', 0):.1f}")
        
        hdg_widget = self.flight_hdg.findChild(QLabel, "value")
        if hdg_widget:
            hdg_widget.setText(f"{telemetry.get('heading', 0):.0f}°")
        
        # Mode
        mode = telemetry.get('flight_mode', 'UNKNOWN')
        self.lbl_mode.setText(mode)
    
    def _get_battery_color(self, percent):
        if percent > 50:
            return "#00ff88"
        elif percent > 25:
            return "#ffa500"
        else:
            return "#ff3333"
    
    def _get_signal_color(self, rssi):
        if rssi > 70:
            return "#00ff88"
        elif rssi > 40:
            return "#ffa500"
        else:
            return "#ff3333"
