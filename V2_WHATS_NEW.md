# ASRA GCS v2.0 - What's New

## 🎉 Multi-Drone Support

ASRA GCS v2.0 introduces support for controlling **up to 2 drones simultaneously** with independent telemetry, color-coded UI, and unified map display.

---

## New Features

### 1. Multi-Drone Connection Manager (`drone_manager.py`)
- Manages multiple MAVLink connections
- Auto-assigns colors to drones (Red, Blue)
- Independent telemetry storage per drone
- Thread-safe state management

### 2. Tabbed Drone Interface (`main_window.py`)
- Each drone gets its own tab
- Add/remove drones via menu or dialog
- Drone count display (0/2, 1/2, 2/2)
- Independent HUD and telemetry per drone

### 3. Individual Drone Panels (`drone_panel_widget.py`)
- Full HUD display
- Complete telemetry (attitude, GPS, battery)
- Control buttons (arm/disarm, set mode)
- Color-coded UI borders matching drone color
- Messages panel with FCU feedback

### 4. Enhanced Map (`professional_gcs_map.py`)
- Multi-drone markers with different colors
- Independent flight paths per drone
- Backward compatible with single-drone mode
- New method: `update_uav_position_multi()`

### 5. New Entry Point (`asra_gcs_v2.py`)
- Launches v2.0 interface
- Displays startup banner
- Initializes map services

---

## Architecture Changes

### Before (v1.0 - Single Drone)
```
asra_gcs_main.py
    ↓
ASRAGCS_UI (gcs_ui.py)
    ↓
Controller
    ↓
MAVLink Worker
```

### After (v2.0 - Multi-Drone)
```
asra_gcs_v2.py
    ↓
MainWindow (main_window.py)
    ↓
DroneManager (drone_manager.py)
    ├→ Drone 1: MAVLink Worker + Controller + Panel
    └→ Drone 2: MAVLink Worker + Controller + Panel
    ↓
Global Map (shows all drones)
```

---

## Usage

### Starting v2.0
```bash
python asra_gcs_v2.py
```

### Adding Drones
1. Click **"+ Add Drone"** button (or Ctrl+N)
2. Select COM port from dropdown
3. Choose baud rate (57600, 115200, 230400)
4. Click "Add"
5. Drone appears in new tab with auto-assigned color

### Removing Drones
- Click **X** on drone tab
- Or: Select tab → Ctrl+W
- Confirm removal dialog

### Switching Views
- **Tabs** (default): Each drone in separate tab
- **Grid** (planned): Side-by-side drone panels

---

## Color Coding

Each drone is automatically assigned a color:
- **Drone 1**: Red (#FF0000)
- **Drone 2**: Blue (#0000FF)

Colors are used for:
- UI panel borders
- Map markers
- Flight paths
- Telemetry labels

---

## Map Features (Multi-Drone)

### Global Map Display
- Shows all connected drones simultaneously
- Each drone has colored marker (matching UI color)
- Independent flight paths
- Drone ID labels on map

### Map Methods
- **Backward Compatible**: `update_uav_position(lat, lon, heading)` (single drone)
- **Multi-Drone**: `update_uav_position_multi(drone_id, lat, lon, heading, alt, speed, color)`

---

## File Changes Summary

### New Files
- `drone_manager.py` - Multi-drone connection manager
- `drone_panel_widget.py` - Individual drone UI panel
- `main_window.py` - Main v2.0 window with tabs
- `asra_gcs_v2.py` - v2.0 entry point
- `MULTI_DRONE_MAP_PATCH.txt` - Map modification notes
- `V2_WHATS_NEW.md` - This file

### Modified Files
- `professional_gcs_map.py` - Added multi-drone support
  - New data structures: `uav_positions`, `flight_paths`
  - New method: `update_uav_position_multi()`
- `main_window.py` - Updated map integration

### Unchanged (v1.0 still works!)
- `asra_gcs_main.py` - Original entry point
- `gcs_ui.py` - Original single-drone UI
- `controller.py` - Works with both v1.0 and v2.0
- `mavlink_worker.py` - Reused per-drone in v2.0

---

## Testing v2.0

### Test Scenarios

**Single Drone**:
1. Launch v2.0
2. Add one drone
3. Connect to SITL or real drone
4. Verify telemetry updates
5. Check map marker appears

**Two Drones**:
1. Launch v2.0
2. Add first drone (Drone 1 - Red)
3. Add second drone (Drone 2 - Blue)
4. Connect both to SITL or real drones
5. Verify independent telemetry in each tab
6. Check both markers appear on global map with different colors
7. Test switching between tabs
8. Verify flight paths are independent

**Stress Test**:
- Run for 10+ minutes with 2 active drones
- Monitor memory usage (<500MB target)
- Check frame rate (30+ FPS target)
- Verify no crashes or freezes

---

## Known Limitations (v2.0.0)

1. **Grid layout not yet implemented** - Only tabs work
2. **Map rendering** - Still uses single _draw_uav method (needs patch)
3. **No drag-and-drop** for drone reordering
4. **Manual map behavior modes** not implemented (follow/show-all/manual)
5. **Flight path drawing** not yet updated for multi-drone colors

---

## Roadmap for v2.1

- [ ] Complete map drawing patches (_draw_uav, _draw_flight_path)
- [ ] Implement grid layout (2x1)
- [ ] Add map behavior toggle (follow/show-all/manual)
- [ ] Drone renaming feature
- [ ] Flight data logging per drone
- [ ] Performance optimizations

---

## Backward Compatibility

**v1.0 is still available!**
- Use `python asra_gcs_main.py` for single-drone v1.0 interface
- All v1.0 features remain functional
- v2.0 does not break v1.0 code

---

## Developer Notes

### Adding More Drones
To support more than 2 drones, change in `main_window.py`:
```python
self.drone_manager = DroneManager(max_drones=4)  # Change from 2 to 4
```

Also update colors in `drone_manager.py`:
```python
DEFAULT_COLORS = [
    "#FF0000",  # Red
    "#0000FF",  # Blue
    "#00FF00",  # Green
    "#FFFF00",  # Yellow
]
```

### Map Integration
Each controller polls its drone's MAVLink worker independently.
The main window's `_update_all_drones()` method:
1. Calls `controller.update_ui()` for each drone
2. Retrieves telemetry from drone_manager
3. Updates global map with `update_uav_position_multi()`

---

## Version Info

- **Version**: 2.0.0
- **Release Date**: January 5, 2026
- **Python**: 3.7+
- **License**: TBD

---

## Upgrade from v1.0

No migration needed! v2.0 runs alongside v1.0.
- Keep using v1.0: `python asra_gcs_main.py`
- Try v2.0: `python asra_gcs_v2.py`

---

**Questions? Issues?**  
Report bugs on GitHub: https://github.com/Zuhaib77/ASRA-GCS/issues
