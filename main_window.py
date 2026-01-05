"""
ASRA GCS - Main Window (v2.0 Multi-Drone)
Main application window with multi-drone support
"""

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QComboBox, QLabel
from drone_manager import DroneManager
from drone_panel_widget import DronePanelWidget
from simple_controller import SimpleController

try:
    from professional_gcs_map import ProfessionalGCSMap
except ImportError:
    ProfessionalGCSMap = None


class MainWindow(QMainWindow):
    """
    Main application window for ASRA GCS v2.0
    Supports multiple drones with tabbed or grid layout
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ASRA GCS v2.0 - Multi-Drone Ground Control Station")
        self.resize(1600, 1000)
        
        # Multi-drone manager
        self.drone_manager = DroneManager(max_drones=2)
        
        # Drone panels (drone_id -> DronePanelWidget)
        self.drone_panels = {}
        
        # Controllers (drone_id -> Controller)
        self.controllers = {}
        
        # Layout mode
        self.layout_mode = "tabs"  # "tabs" or "grid"
        
        # Setup UI
        self._create_menu_bar()
        self._create_ui()
        
        # Timer for polling telemetry
        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self._update_all_drones)
        self.update_timer.start(100)  # 10 Hz
        
    def _create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        exit_action = QtWidgets.QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        toggle_layout_action = QtWidgets.QAction("Toggle &Layout (Tabs/Grid)", self)
        toggle_layout_action.setShortcut("Ctrl+L")
        toggle_layout_action.triggered.connect(self._toggle_layout)
        view_menu.addAction(toggle_layout_action)
        
        # Drone menu
        drone_menu = menubar.addMenu("&Drone")
        
        add_drone_action = QtWidgets.QAction("&Add Drone", self)
        add_drone_action.setShortcut("Ctrl+N")
        add_drone_action.triggered.connect(self._show_add_drone_dialog)
        drone_menu.addAction(add_drone_action)
        
        remove_drone_action = QtWidgets.QAction("&Remove Current Drone", self)
        remove_drone_action.setShortcut("Ctrl+W")
        remove_drone_action.triggered.connect(self._remove_current_drone)
        drone_menu.addAction(remove_drone_action)
        
    def _create_ui(self):
        """Create main UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Top: Drone tabs/grid
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        
        # Create tab widget
        self.drone_tabs = QTabWidget()
        self.drone_tabs.setTabsClosable(True)
        self.drone_tabs.tabCloseRequested.connect(self._close_drone_tab)
        
        self.content_layout.addWidget(self.drone_tabs)
        
        main_layout.addWidget(self.content_widget, stretch=3)
        
        # Bottom: Global map
        self.map_widget = self._create_map_widget()
        if self.map_widget:
            map_container = QWidget()
            map_layout = QVBoxLayout(map_container)
            map_header = QLabel("<b>Global Map - All Drones</b>")
            map_header.setStyleSheet("background: #333; padding: 5px; color: #0FF;")
            map_layout.addWidget(map_header)
            map_layout.addWidget(self.map_widget)
            main_layout.addWidget(map_container, stretch=2)
        
        # Connection toolbar
        self._create_connection_toolbar(main_layout)
        
        # Apply dark theme
        self._apply_theme()
        
    def _create_map_widget(self):
        """Create global map widget"""
        if ProfessionalGCSMap:
            return ProfessionalGCSMap()
        else:
            placeholder = QLabel("Map Widget (Loading...)")
            placeholder.setStyleSheet("background: #2a2a2a; color: white; padding: 20px;")
            placeholder.setAlignment(QtCore.Qt.AlignCenter)
            return placeholder
    
    def _create_connection_toolbar(self, parent_layout):
        """Create connection controls toolbar"""
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar.setStyleSheet("background: #1a1a1a; padding: 5px;")
        
        # Add drone button
        self.btn_add_drone = QPushButton("+ Add Drone")
        self.btn_add_drone.clicked.connect(self._show_add_drone_dialog)
        toolbar_layout.addWidget(self.btn_add_drone)
        
        # Drone count label
        self.lbl_drone_count = QLabel("Drones: 0/2")
        self.lbl_drone_count.setStyleSheet("color: #0FF; font-weight: bold;")
        toolbar_layout.addWidget(self.lbl_drone_count)
        
        toolbar_layout.addStretch()
        
        # Layout toggle
        self.btn_layout_toggle = QPushButton("Switch to Grid")
        self.btn_layout_toggle.clicked.connect(self._toggle_layout)
        toolbar_layout.addWidget(self.btn_layout_toggle)
        
        parent_layout.addWidget(toolbar)
    
    def _show_add_drone_dialog(self):
        """Show dialog to add a new drone"""
        if not self.drone_manager.can_add_drone():
            QtWidgets.QMessageBox.warning(
                self, "Maximum Drones",
                f"Maximum number of drones ({self.drone_manager.max_drones}) already added."
            )
            return
        
        # Get available ports
        import serial.tools.list_ports
        ports = [f"{p.device} - {p.description}" for p in serial.tools.list_ports.comports()]
        
        if not ports:
            ports = ["No ports detected"]
        
        # Create dialog
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Add Drone")
        dialog_layout = QVBoxLayout(dialog)
        
        # Port selection
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Port:"))
        port_combo = QComboBox()
        port_combo.addItems(ports)
        port_layout.addWidget(port_combo)
        dialog_layout.addLayout(port_layout)
        
        # Baud rate
        baud_layout = QHBoxLayout()
        baud_layout.addWidget(QLabel("Baud:"))
        baud_combo = QComboBox()
        baud_combo.addItems(["57600", "115200", "230400"])
        baud_layout.addWidget(baud_combo)
        dialog_layout.addLayout(baud_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        btn_ok = QPushButton("Add")
        btn_cancel = QPushButton("Cancel")
        btn_ok.clicked.connect(dialog.accept)
        btn_cancel.clicked.connect(dialog.reject)
        button_layout.addWidget(btn_ok)
        button_layout.addWidget(btn_cancel)
        dialog_layout.addLayout(button_layout)
        
        # Show dialog
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            port = port_combo.currentText()
            baud = int(baud_combo.currentText())
            self._add_drone(port, baud)
    
    def _add_drone(self, port, baud):
        """Add a new drone"""
        # Add to drone manager
        drone_id = self.drone_manager.add_drone(port, baud)
        
        if drone_id is None:
            QtWidgets.QMessageBox.warning(self, "Error", "Failed to add drone")
            return
        
        # Create drone panel
        panel = DronePanelWidget(drone_id, self.drone_manager, self)
        self.drone_panels[drone_id] = panel
        
        # Create controller for this drone
        drone = self.drone_manager.get_drone(drone_id)
        controller = SimpleController(panel, drone.worker)
        self.controllers[drone_id] = controller
        
        # Add tab
        drone_name = drone.name if drone else f"Drone {len(self.drone_panels)}"
        self.drone_tabs.addTab(panel, f"● {drone_name}")
        
        # Update count
        self._update_drone_count()
        
        # Auto-connect
        self.drone_manager.connect_drone(drone_id)
        
    def _remove_current_drone(self):
        """Remove currently selected drone"""
        current_index = self.drone_tabs.currentIndex()
        if current_index < 0:
            return
        
        self._close_drone_tab(current_index)
    
    def _close_drone_tab(self, index):
        """Close drone tab and remove drone"""
        # Get drone ID from tab
        widget = self.drone_tabs.widget(index)
        if not isinstance(widget, DronePanelWidget):
            return
        
        drone_id = widget.drone_id
        
        # Confirm
        reply = QtWidgets.QMessageBox.question(
            self, "Remove Drone",
            f"Are you sure you want to remove this drone?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply != QtWidgets.QMessageBox.Yes:
            return
        
        # Remove from manager
        self.drone_manager.remove_drone(drone_id)
        
        # Remove tab
        self.drone_tabs.removeTab(index)
        
        # Remove from dicts
        if drone_id in self.drone_panels:
            del self.drone_panels[drone_id]
        if drone_id in self.controllers:
            del self.controllers[drone_id]
        
        # Update count
        self._update_drone_count()
    
    def _update_drone_count(self):
        """Update drone count label"""
        count = self.drone_manager.get_drone_count()
        max_count = self.drone_manager.max_drones
        self.lbl_drone_count.setText(f"Drones: {count}/{max_count}")
        
        # Enable/disable add button
        self.btn_add_drone.setEnabled(count < max_count)
    
    def _toggle_layout(self):
        """Toggle between tabs and grid layout"""
        if self.layout_mode == "tabs":
            self.layout_mode = "grid"
            self.btn_layout_toggle.setText("Switch to Tabs")
            self._create_grid_layout()
        else:
            self.layout_mode = "tabs"
            self.btn_layout_toggle.setText("Switch to Grid")
            self._create_tabbed_layout()
    
    def _create_grid_layout(self):
        """Create grid layout (2x1 for 2 drones)"""
        # TODO: Implement grid layout
        # For now, just show message
        QtWidgets.QMessageBox.information(
            self, "Grid Layout",
            "Grid layout coming soon! For now, using tabs."
        )
    
    def _create_tabbed_layout(self):
        """Recreate tabbed layout"""
        # Already in tabbed layout
        pass
    
    def _update_all_drones(self):
        """Update telemetry for all drones"""
        for drone_id, controller in self.controllers.items():
            # Poll worker queue
            controller.update_ui()
            
            # Update map with drone positions using multi-drone method
            drone = self.drone_manager.get_drone(drone_id)
            if drone and hasattr(self.map_widget, 'update_uav_position_multi'):
                gps_data = drone.telemetry.get('gps', {})
                lat = gps_data.get('lat', 0)
                lon = gps_data.get('lon', 0)
                
                attitude_data = drone.telemetry.get('attitude', {})
                import math
                yaw = attitude_data.get('yaw', 0)
                heading = math.degrees(yaw)
                
                vfr_data = drone.telemetry.get('vfr_hud', {})
                altitude = vfr_data.get('alt', 0)
                speed = vfr_data.get('groundspeed', 0)
                
                if lat != 0 or lon != 0:
                    self.map_widget.update_uav_position_multi(
                        drone_id, lat, lon, heading, altitude, speed, drone.color
                    )
    
    def _apply_theme(self):
        """Apply dark theme"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2a2a2a;
            }
            QPushButton {
                background-color: #0078d4;
                border: 1px solid #005a9e;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
            QLabel {
                color: #ffffff;
            }
        """)
    
    def closeEvent(self, event):
        """Clean up on close"""
        # Stop update timer
        self.update_timer.stop()
        
        # Cleanup drone manager
        self.drone_manager.cleanup()
        
        # Stop all controllers
        for controller in self.controllers.values():
            if hasattr(controller, 'timer'):
                controller.timer.stop()
        
        event.accept()
