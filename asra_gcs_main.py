#!/usr/bin/env python3
"""
ASRA Ground Control Station - Final Clean Version
Professional UAV Ground Control Station with satellite imagery
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

def main():
    """Main application entry point"""
    
    print("=" * 60)
    print("ASRA Ground Control Station")
    print("Professional UAV Ground Control & Monitoring")
    print("=" * 60)
    print()
    print("Features:")
    print("Professional Mission Planner interface")
    print("Esri World Imagery satellite maps (FREE)")
    print("Real-time UAV tracking & telemetry")
    print("Artificial horizon HUD")
    print("MAVLink communication")
    print("Mission planning & waypoints")
    print("Offline map caching")
    print()
    print("Starting ASRA GCS...")
    print("-" * 60)
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("ASRA Ground Control Station")
    app.setApplicationVersion("2.0")
    
    try:
        # Import main UI
        from gcs_ui import ASRAGCS_UI
        
        # Create main window
        gcs = ASRAGCS_UI()
        gcs.resize(1600, 1000)
        gcs.show()
        
        # Start tile downloader after UI is shown (prevents Qt conflicts)
        def start_map_services():
            if hasattr(gcs, 'map_widget') and gcs.map_widget:
                if hasattr(gcs.map_widget, 'tile_downloader'):
                    if not gcs.map_widget.tile_downloader.isRunning():
                        gcs.map_widget.tile_downloader.start()
                        print("Map tile downloader started")
                # Request initial tiles
                if hasattr(gcs.map_widget, '_request_visible_tiles'):
                    gcs.map_widget._request_visible_tiles()
        
        # Start map services after short delay
        QTimer.singleShot(500, start_map_services)
        
        print("ASRA GCS started successfully!")
        print("Satellite imagery loading...")
        print("All controls functional")
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