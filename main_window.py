"""
ASRA GCS - Main Window (v2.0 Redesigned)
New layout matching React UI design:
- Left sidebar: Connection controls
- Main area: 3 tabs (Combined, Drone 1, Drone 2)
- Combined view: Status cards + HUDs | Map + Comparison | Telemetry
"""

import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, 
                            QWidget, QSplitter, QGridLayout, QScrollArea, QLabel)
from PyQt5.QtCore import Qt

from drone_manager import DroneManager
from drone_panel_widget import DronePanelWidget
from drone_status_card import DroneStatusCard
from connection_sidebar import ConnectionSidebar
from comparison_panel import ComparisonPanel
from simple_controller import SimpleController

try:
    from professional_gcs_map import ProfessionalGCSMap
    from hud_widget_reference_style import ReferenceStyleHUDWidget
except ImportError:
    ProfessionalGCSMap = None
    ReferenceStyleHUDWidget = None


class MainWindow(QMainWindow):
    """Main window with redesigned layout"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ASRA GCS v2.0 - Multi-Drone Ground Control Station")
        self.resize(1800, 1000)
        
        # Drone manager
        self.drone_manager = DroneManager(max_drones=2)
        
        # Pre-create drones
        self.drone_1_id = self.drone_manager.add_drone("", 57600, "Drone 1")
        self.drone_2_id = self.drone_manager.add_drone("", 57600, "Drone 2")
        
        # Controllers
        self.controllers = {}
        
        # UI components
        self.status_cards = {}
        self.mini_huds = {}
        
        # Setup UI
        self._create_ui()
        
        # Telemetry update timer
        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self._update_all_drones)
        self.update_timer.start(100)  # 10 Hz
        
    def _create_ui(self):
        """Create main UI with sidebar + tabs"""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main horizontal splitter: Sidebar | Content
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setChildrenCollapsible(False)
        
        # Left: Connection sidebar
        self.sidebar = ConnectionSidebar(self.drone_manager, self)
        self.sidebar.connect_requested.connect(self._on_connect_drone)
        self.sidebar.disconnect_requested.connect(self._on_disconnect_drone)
        main_splitter.addWidget(self.sidebar)
        
        # Right: Main content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(12, 12, 12, 12)
        content_layout.setSpacing(8)
        
        # Tabs
        self.main_tabs = QTabWidget()
        self.main_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #2a2a2a;
                background: #0a0a0a;
                border-radius: 6px;
            }
            QTabBar::tab {
                background: #1a1a1a;
                color: #9ca3af;
                padding: 10px 20px;
                margin-right: 4px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #00d4ff20;
                color: #00d4ff;
            }
            QTabBar::tab:hover {
                background: #2a2a2a;
            }
        """)
        
        # Tab 1: Combined View
        combined_tab = self._create_combined_tab()
        self.main_tabs.addTab(combined_tab, "● Combined View")
        
        # Tab 2: Drone 1
        drone1_tab = self._create_individual_tab(self.drone_1_id, "Drone 1", "#00d4ff")
        self.main_tabs.addTab(drone1_tab, "Drone 1")
        
        # Tab 3: Drone 2
        drone2_tab = self._create_individual_tab(self.drone_2_id, "Drone 2", "#a78bfa")
        self.main_tabs.addTab(drone2_tab, "Drone 2")
        
        content_layout.addWidget(self.main_tabs)
        main_splitter.addWidget(content_widget)
        
        # Set splitter sizes
        main_splitter.setSizes([250, 1550])
        
        # Set as central layout
        central_layout = QHBoxLayout(central)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.addWidget(main_splitter)
        
        # Apply theme
        self._apply_theme()
        
    def _create_combined_tab(self):
        """Create Combined view with 3-column grid"""
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(8)
        
        # 3-column grid
        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setColumnStretch(0, 4)  # Left: Status + HUDs
        grid.setColumnStretch(1, 5)  # Center: Map + Compare
        grid.setColumnStretch(2, 3)  # Right: Telemetry
        
        # === LEFT COLUMN: Status Cards + Mini HUDs ===
        left_column = QWidget()
        left_layout = QVBoxLayout(left_column)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)
        
        #Drone 1 Status Card
        card1 = DroneStatusCard(self.drone_1_id, self.drone_manager, "#00d4ff")
        card1.arm_clicked.connect(self._on_arm_disarm)
        self.status_cards[self.drone_1_id] = card1
        left_layout.addWidget(card1)
        
        # Drone 1 Full HUD
        if ReferenceStyleHUDWidget:
            hud1 = ReferenceStyleHUDWidget()
            hud1.setFixedSize(400, 350)
            self.mini_huds[self.drone_1_id] = hud1
            left_layout.addWidget(hud1)
        
        # Drone 2 Status Card
        card2 = DroneStatusCard(self.drone_2_id, self.drone_manager, "#a78bfa")
        card2.arm_clicked.connect(self._on_arm_disarm)
        self.status_cards[self.drone_2_id] = card2
        left_layout.addWidget(card2)
        
        # Drone 2 Full HUD
        if ReferenceStyleHUDWidget:
            hud2 = ReferenceStyleHUDWidget()
            hud2.setFixedSize(400, 350)
            self.mini_huds[self.drone_2_id] = hud2
            left_layout.addWidget(hud2)
        
        left_layout.addStretch()
        
        # Scroll area for left column
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setWidget(left_column)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        left_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        grid.addWidget(left_scroll, 0, 0)
        
        # === CENTER COLUMN: Map + Comparison ===
        center_column = QWidget()
        center_layout = QVBoxLayout(center_column)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(12)
        
        # Map
        if not hasattr(self, 'map_widget'):
            self.map_widget = self._create_map_widget()
        
        map_container = QWidget()
        map_container.setStyleSheet("background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 6px;")
        map_layout = QVBoxLayout(map_container)
        map_layout.setContentsMargins(0, 0, 0, 0)
        map_layout.setSpacing(0)
        
        map_header = QLabel("  🗺️ Global Map - Both Drones")
        map_header.setStyleSheet("""
            background: #0a0a0a;
            color: #00d4ff;
            font-size: 11pt;
            font-weight: bold;
            padding: 8px;
            border-bottom: 1px solid #2a2a2a;
        """)
        map_layout.addWidget(map_header)
        map_layout.addWidget(self.map_widget, 1)
        
        center_layout.addWidget(map_container, 3)
        
        # Comparison Panel
        self.comparison_panel = ComparisonPanel()
        center_layout.addWidget(self.comparison_panel, 1)
        
        grid.addWidget(center_column, 0, 1)
        
        # === RIGHT COLUMN: Telemetry Messages ===
        right_column = QWidget()
        right_column.setStyleSheet("background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 6px;")
        right_layout = QVBoxLayout(right_column)
        right_layout.setContentsMargins(0,0, 0, 0)
        right_layout.setSpacing(0)
        
        tel_header = QLabel("  📡 Telemetry Messages")
        tel_header.setStyleSheet("""
            background: #0a0a0a;
            color: #00d4ff;
            font-size: 11pt;
            font-weight: bold;
            padding: 8px;
            border-bottom: 1px solid #2a2a2a;
        """)
        right_layout.addWidget(tel_header)
        
        self.telemetry_messages = QtWidgets.QTextEdit()
        self.telemetry_messages.setReadOnly(True)
        self.telemetry_messages.setStyleSheet("""
            QTextEdit {
                background: #0a0a0a;
                border: none;
                color: #9ca3af;
                font-family: 'Consolas', monospace;
                font-size: 9pt;
                padding: 8px;
            }
        """)
        right_layout.addWidget(self.telemetry_messages, 1)
        
        grid.addWidget(right_column, 0, 2)
        
        container_layout.addLayout(grid)
        
        return container
    
    def _create_individual_tab(self, drone_id, name, color):
        """Create individual drone tab"""
        panel = DronePanelWidget(drone_id, self.drone_manager, self)
        
        # Create controller if not exists
        if drone_id not in self.controllers:
            drone = self.drone_manager.get_drone(drone_id)
            self.controllers[drone_id] = SimpleController(panel, drone.worker)
        
        return panel
    
    def _create_map_widget(self):
        """Create map widget"""
        if ProfessionalGCSMap:
            return ProfessionalGCSMap()
        else:
            placeholder = QLabel("Map (Loading...)")
            placeholder.setStyleSheet("background: #0a0a0a; color: #9ca3af; padding: 20px;")
            placeholder.setAlignment(Qt.AlignCenter)
            return placeholder
    
    def _on_connect_drone(self, drone_id, port, baud):
        """Handle drone connection from sidebar"""
        drone = self.drone_manager.get_drone(drone_id)
        if drone:
            drone.port = port
            drone.baud = baud
            drone.worker.configure(port, baud)
            self.drone_manager.connect_drone(drone_id)
            self.telemetry_messages.append(f"[{drone.name}] Connecting to {port} @ {baud}...")
    
    def _on_disconnect_drone(self, drone_id):
        """Handle drone disconnection from sidebar"""
        self.drone_manager.disconnect_drone(drone_id)
        drone = self.drone_manager.get_drone(drone_id)
        if drone:
            self.telemetry_messages.append(f"[{drone.name}] Disconnected")
    
    def _on_arm_disarm(self, drone_id):
        """Handle arm/disarm from status card"""
        drone = self.drone_manager.get_drone(drone_id)
        if drone and drone.connected:
            self.drone_manager.send_command(drone_id, 'arm_disarm')
            self.telemetry_messages.append(f"[{drone.name}] Arm/Disarm command sent")
        else:
            self.telemetry_messages.append(f"[{drone.name}] Not connected!")
    
    def _update_all_drones(self):
        """Update telemetry for all drones"""
        drone1 = self.drone_manager.get_drone(self.drone_1_id)
        drone2 = self.drone_manager.get_drone(self.drone_2_id)
        
        # Update controllers
        for drone_id, controller in self.controllers.items():
            controller.update_ui()
        
        # Update sidebar connection status
        if drone1:
            self.sidebar.update_connection_status(self.drone_1_id, drone1.connected)
        if drone2:
            self.sidebar.update_connection_status(self.drone_2_id, drone2.connected)
        
        #Update status cards
        if drone1 and self.drone_1_id in self.status_cards:
            self.status_cards[self.drone_1_id].update_status(drone1.telemetry)
        if drone2 and self.drone_2_id in self.status_cards:
            self.status_cards[self.drone_2_id].update_status(drone2.telemetry)
        
        # Update mini HUDs
        if drone1 and self.drone_1_id in self.mini_huds:
            att = drone1.telemetry.get('attitude', {})
            vfr = drone1.telemetry.get('vfr_hud', {})
            gps = drone1.telemetry.get('gps', {})
            self.mini_huds[self.drone_1_id].update_attitude(att.get('roll', 0), att.get('pitch', 0), att.get('yaw', 0))
            self.mini_huds[self.drone_1_id].update_vfr(vfr.get('heading', 0), vfr.get('airspeed', 0), 
                                                       vfr.get('groundspeed', 0), vfr.get('alt', 0))
        
        if drone2 and self.drone_2_id in self.mini_huds:
            att = drone2.telemetry.get('attitude', {})
            vfr = drone2.telemetry.get('vfr_hud', {})
            self.mini_huds[self.drone_2_id].update_attitude(att.get('roll', 0), att.get('pitch', 0), att.get('yaw', 0))
            self.mini_huds[self.drone_2_id].update_vfr(vfr.get('heading', 0), vfr.get('airspeed', 0), 
                                                       vfr.get('groundspeed', 0), vfr.get('alt', 0))
        
        # Update comparison panel
        if drone1 and drone2:
            self.comparison_panel.update_comparison(drone1.telemetry, drone2.telemetry)
        
        # Update map
        if drone1 and drone1.connected and hasattr(self.map_widget, 'update_uav_position_multi'):
            gps = drone1.telemetry.get('gps', {})
            att = drone1.telemetry.get('attitude', {})
            vfr = drone1.telemetry.get('vfr_hud', {})
            
            lat = gps.get('lat', 0)
            lon = gps.get('lon', 0)
            if lat != 0 or lon != 0:
                import math
                heading = math.degrees(att.get('yaw', 0))
                self.map_widget.update_uav_position_multi(
                    self.drone_1_id, lat, lon, heading, 
                    vfr.get('alt', 0), vfr.get('groundspeed', 0), "#00d4ff"
                )
        
        if drone2 and drone2.connected and hasattr(self.map_widget, 'update_uav_position_multi'):
            gps = drone2.telemetry.get('gps', {})
            att = drone2.telemetry.get('attitude', {})
            vfr = drone2.telemetry.get('vfr_hud', {})
            
            lat = gps.get('lat', 0)
            lon = gps.get('lon', 0)
            if lat != 0 or lon != 0:
                import math
                heading = math.degrees(att.get('yaw', 0))
                self.map_widget.update_uav_position_multi(
                    self.drone_2_id, lat, lon, heading,
                    vfr.get('alt', 0), vfr.get('groundspeed', 0), "#a78bfa"
                )
    
    def _apply_theme(self):
        """Apply dark theme"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0a0a;
            }
            QWidget {
                background-color: #0a0a0a;
                color: #ffffff;
            }
        """)
    
    def closeEvent(self, event):
        """Clean up on close"""
        self.update_timer.stop()
        self.drone_manager.cleanup()
        event.accept()
