"""
ASRA GCS - Comparison Panel Widget
Side-by-side comparison of two drones
Matches React UI design
"""

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel


class ComparisonPanel(QWidget):
    """
    Comparison panel showing both drones side-by-side
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        """Create comparison UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Panel styling
        self.setStyleSheet("""
            ComparisonPanel {
                background-color: #1a1a1a;
                border: 1px solid #2a2a2a;
                border-radius: 6px;
            }
            QLabel {
                color: #9ca3af;
            }
        """)
        
        # Header
        header = QHBoxLayout()
        icon = QLabel("📊")
        icon.setStyleSheet("font-size: 14pt;")
        title = QLabel("Comparison")
        title.setStyleSheet("color: white; font-size: 11pt; font-weight: bold;")
        header.addWidget(icon)
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)
        
        # Comparison grid
        grid = QGridLayout()
        grid.setSpacing(12)
        
        # Drone 1 column
        drone1_header = QHBoxLayout()
        d1_dot = QLabel()
        d1_dot.setFixedSize(8, 8)
        d1_dot.setStyleSheet("background-color: #00d4ff; border-radius: 4px;")
        d1_label = QLabel("ALPHA")
        d1_label.setStyleSheet("color: #9ca3af; font-size: 9pt; font-weight: bold; font-family: 'Consolas', monospace;")
        drone1_header.addWidget(d1_dot)
        drone1_header.addWidget(d1_label)
        drone1_header.addStretch()
        
        drone1_widget = QWidget()
        drone1_layout = QVBoxLayout(drone1_widget)
        drone1_layout.setContentsMargins(0, 0, 0, 0)
        drone1_layout.setSpacing(4)
        drone1_layout.addLayout(drone1_header)
        
        self.d1_altitude = self._create_metric_row("Altitude", "0m")
        self.d1_speed = self._create_metric_row("Speed", "0m/s")
        self.d1_battery = self._create_metric_row("Battery", "100%")
        
        drone1_layout.addLayout(self.d1_altitude)
        drone1_layout.addLayout(self.d1_speed)
        drone1_layout.addLayout(self.d1_battery)
        
        grid.addWidget(drone1_widget, 0, 0)
        
        # Drone 2 column
        drone2_header = QHBoxLayout()
        d2_dot = QLabel()
        d2_dot.setFixedSize(8, 8)
        d2_dot.setStyleSheet("background-color: #a78bfa; border-radius: 4px;")
        d2_label = QLabel("BRAVO")
        d2_label.setStyleSheet("color: #9ca3af; font-size: 9pt; font-weight: bold; font-family: 'Consolas', monospace;")
        drone2_header.addWidget(d2_dot)
        drone2_header.addWidget(d2_label)
        drone2_header.addStretch()
        
        drone2_widget = QWidget()
        drone2_layout = QVBoxLayout(drone2_widget)
        drone2_layout.setContentsMargins(0, 0, 0, 0)
        drone2_layout.setSpacing(4)
        drone2_layout.addLayout(drone2_header)
        
        self.d2_altitude = self._create_metric_row("Altitude", "0m")
        self.d2_speed = self._create_metric_row("Speed", "0m/s")
        self.d2_battery = self._create_metric_row("Battery", "100%")
        
        drone2_layout.addLayout(self.d2_altitude)
        drone2_layout.addLayout(self.d2_speed)
        drone2_layout.addLayout(self.d2_battery)
        
        grid.addWidget(drone2_widget, 0, 1)
        
        layout.addLayout(grid)
        
    def _create_metric_row(self, label, value):
        """Create metric display row"""
        row = QHBoxLayout()
        row.setSpacing(8)
        
        lbl = QLabel(label)
        lbl.setStyleSheet("color: #9ca3af; font-size: 9pt;")
        
        val = QLabel(value)
        val.setObjectName("value")
        val.setStyleSheet("color: white; font-size: 9pt; font-weight: bold; font-family: 'Consolas', monospace;")
        
        row.addWidget(lbl)
        row.addStretch()
        row.addWidget(val)
        
        return row
    
    def update_comparison(self, drone1_data, drone2_data):
        """Update comparison with drone data"""
        # Drone 1
        self._update_metric(self.d1_altitude, f"{drone1_data.get('altitude_agl', 0):.1f}m")
        self._update_metric(self.d1_speed, f"{drone1_data.get('ground_speed', 0):.1f}m/s")
        self._update_metric(self.d1_battery, f"{drone1_data.get('battery_percent', 0):.0f}%")
        
        # Drone 2
        self._update_metric(self.d2_altitude, f"{drone2_data.get('altitude_agl', 0):.1f}m")
        self._update_metric(self.d2_speed, f"{drone2_data.get('ground_speed', 0):.1f}m/s")
        self._update_metric(self.d2_battery, f"{drone2_data.get('battery_percent', 0):.0f}%")
    
    def _update_metric(self, layout, value):
        """Update metric value"""
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if widget and widget.objectName() == "value":
                widget.setText(value)
                break
