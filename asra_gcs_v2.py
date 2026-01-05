#!/usr/bin/env python3
"""
ASRA Ground Control Station v2.0 - Multi-Drone Support
Professional UAV Ground Control Station with multi-drone capability
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

def main():
    """Main application entry point"""
    
    print("=" * 60)
    print("ASRA Ground Control Station v2.0")
    print("Multi-Drone Professional Ground Control")
    print("=" * 60)
    print()
    print("Features:")
    print("✓ Multi-drone support (up to 2 drones)")
    print("✓ Tabbed drone interface")
    print("✓ Global map with all drones")
    print("✓ Independent telemetry per drone")
    print("✓ Color-coded drone markers")
    print("✓ Real-time position tracking")
    print("✓ MAVLink communication")
    print("✓ Offline map caching")
    print()
    print("Starting ASRA GCS v2.0...")
    print("-" * 60)
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("ASRA Ground Control Station v2.0")
    app.setApplicationVersion("2.0.0")
    
    try:
        # Import main window
        from main_window import MainWindow
        
        # Create main window
        window = MainWindow()
        window.show()
        
        # Start map services after UI is shown
        def start_map_services():
            if hasattr(window, 'map_widget') and window.map_widget:
                if hasattr(window.map_widget, 'tile_downloader'):
                    if not window.map_widget.tile_downloader.isRunning():
                        window.map_widget.tile_downloader.start()
                        print("Map tile downloader started")
                # Request initial tiles
                if hasattr(window.map_widget, '_request_visible_tiles'):
                    window.map_widget._request_visible_tiles()
        
        # Start map services after short delay
        QTimer.singleShot(500, start_map_services)
        
        print("ASRA GCS v2.0 started successfully!")
        print("Use Ctrl+N or menu to add drones")
        print("Global map shows all connected drones")
        print("Close the window to exit.")
        
        # Run Qt event loop
        return app.exec_()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nApplication interrupted")
        sys.exit(0)
    except Exception as e:
        print(f"Critical error: {e}")
        sys.exit(1)
