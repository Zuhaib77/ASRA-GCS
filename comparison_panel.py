"""
ASRA GCS - Comparison Panel Widget (Refined)
Properly measured with no overlapping text
"""

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel


class ComparisonPanel(QWidget):
    """
    Comparison panel - refined with fixed sizing
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(120)
        self.setMaximumHeight(150)
        self._setup_ui()
        
    def _setup_ui(self):
        """Create UI with precise measurements"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        self.setStyleSheet("""
            ComparisonPanel {
                background-color: #1a1a1a;
                border: 1px solid #2a2a2a;
                border-radius: 6px;
            }
        """)
        
        # Header (fixed height: 24px)
        header = QHBoxLayout()
        header.setSpacing(6)
        header.setContentsMargins(0, 0, 0, 0)
        
        icon = QLabel("📊")
        icon.setFixedSize(16, 16)
        icon.setStyleSheet("font-size: 12pt;")
        
        title = QLabel("Comparison")
        title.setFixedHeight(18)
        title.setStyleSheet("color: white; font-size: 10pt; font-weight: bold;")
        
        header.addWidget(icon)
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)
        
        # Comparison grid (2 columns, fixed content)
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setContentsMargins(0, 0, 0, 0)
        
        # Drone 1 column
        d1_widget = self._create_drone_column("ALPHA", "#00d4ff")
        self.d1_altitude = d1_widget[0]
        self.d1_speed = d1_widget[1]
        self.d1_battery = d1_widget[2]
        
        grid.addWidget(d1_widget[3], 0, 0)
        
        # Drone 2 column
        d2_widget = self._create_drone_column("BRAVO", "#a78bfa")
        self.d2_altitude = d2_widget[0]
        self.d2_speed = d2_widget[1]
        self.d2_battery = d2_widget[2]
        
        grid.addWidget(d2_widget[3], 0, 1)
        
        layout.addLayout(grid)
        
    def _create_drone_column(self, name, color):
        """Create comparison column for one drone"""
        container = QWidget()
        container.setFixedHeight(70)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Header
        header = QHBoxLayout()
        header.setSpacing(4)
        
        dot = QLabel()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(f"background-color: {color}; border-radius: 4px;")
        
        label = QLabel(name)
        label.setFixedHeight(14)
        label.setStyleSheet("color: #9ca3af; font-size: 8pt; font-weight: bold; font-family: 'Consolas', monospace;")
        
        header.addWidget(dot)
        header.addWidget(label)
        header.addStretch()
        layout.addLayout(header)
        
        # Metrics (3 fixed-height rows)
        alt_row = self._create_metric_row("Alt", "0m")
        spd_row = self._create_metric_row("Spd", "0m/s")
        bat_row = self._create_metric_row("Bat", "100%")
        
        layout.addLayout(alt_row)
        layout.addLayout(spd_row)
        layout.addLayout(bat_row)
        
        return (alt_row, spd_row, bat_row, container)
    
    def _create_metric_row(self, label, value):
        """Create metric row with fixed sizing"""
        row = QHBoxLayout()
        row.setSpacing(6)
        row.setContentsMargins(0, 0, 0, 0)
        
        lbl = QLabel(label)
        lbl.setFixedWidth(30)
        lbl.setFixedHeight(14)
        lbl.setStyleSheet("color: #9ca3af; font-size: 8pt;")
        
        val = QLabel(value)
        val.setObjectName("value")
        val.setFixedHeight(14)
        val.setAlignment(Qt.AlignRight)
        val.setStyleSheet("color: white; font-size: 8pt; font-weight: bold; font-family: 'Consolas', monospace;")
        
        row.addWidget(lbl)
        row.addStretch()
        row.addWidget(val)
        
        return row
    
    def update_comparison(self, drone1_data, drone2_data):
        """Update comparison with drone data"""
        # Drone 1
        alt1 = drone1_data.get('altitude_agl', 0)
        self._update_metric(self.d1_altitude, f"{alt1:.0f}m" if alt1 < 1000 else f"{alt1/1000:.1f}km")
        
        spd1 = drone1_data.get('ground_speed', 0)
        self._update_metric(self.d1_speed, f"{spd1:.1f}m/s")
        
        bat1 = drone1_data.get('battery_percent', 0)
        self._update_metric(self.d1_battery, f"{bat1:.0f}%")
        
        # Drone 2
        alt2 = drone2_data.get('altitude_agl', 0)
        self._update_metric(self.d2_altitude, f"{alt2:.0f}m" if alt2 < 1000 else f"{alt2/1000:.1f}km")
        
        spd2 = drone2_data.get('ground_speed', 0)
        self._update_metric(self.d2_speed, f"{spd2:.1f}m/s")
        
        bat2 = drone2_data.get('battery_percent', 0)
        self._update_metric(self.d2_battery, f"{bat2:.0f}%")
    
    def _update_metric(self, layout, value):
        """Update metric value"""
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if widget and widget.objectName() == "value":
                widget.setText(value)
                break
