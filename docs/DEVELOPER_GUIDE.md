# ASRA GCS - Developer Guide

> **For**: Contributors, developers, and anyone modifying the codebase  
> **Version**: 1.0.0  
> **Last Updated**: January 5, 2026

---

## Table of Contents

1. [Development Setup](#development-setup)
2. [Architecture Overview](#architecture-overview)
3. [Code Structure](#code-structure)
4. [Key Components](#key-components)
5. [Build & Deployment](#build--deployment)
6. [Contributing Guidelines](#contributing-guidelines)
7. [Testing](#testing)
8. [Performance Optimization](#performance-optimization)

---

## Development Setup

### Prerequisites

- **Python**: 3.7 or higher
- **Git**: For version control
- **IDE**: VS Code, PyCharm, or your preference
- **Flight Controller/SITL**: For testing (optional but recommended)

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/Zuhaib77/ASRA-GCS.git
cd ASRA-GCS

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python asra_gcs_main.py
```

### Development Dependencies

Create `requirements-dev.txt`:
```
# Testing
pytest>=7.0.0
pytest-cov>=3.0.0
pytest-qt>=4.0.0

# Code Quality
black>=22.0.0
flake8>=4.0.0
pylint>=2.12.0

# Documentation
sphinx>=4.4.0
sphinx-rtd-theme>=1.0.0
```

Install: `pip install -r requirements-dev.txt`

---

## Architecture Overview

### Design Philosophy

ASRA GCS follows a **Model-View-Controller (MVC)** pattern with additional threading for MAVLink communication:

```
┌─────────────────────────────────────────┐
│         Main Application Loop           │
│         (asra_gcs_main.py)             │
└──────────────┬──────────────────────────┘
               │
      ┌────────▼─────────┐
      │   Controller     │
      │ (controller.py)  │
      └────┬─────────┬───┘
           │         │
    ┌──────▼───┐  ┌─▼────────────┐
    │   View   │  │   Model      │
    │ (gcs_ui) │  │ (MAVLink)    │
    └──────────┘  └──────────────┘
```

### Threading Model

- **Main Thread**: Qt GUI event loop (UI updates, user interactions)
- **MAVLink Worker Thread**: Handles serial/UDP communication, message parsing
- **Tile Downloader Thread**: Background map tile downloading

All inter-thread communication uses **Qt Signals/Slots** for thread safety.

### Data Flow

```
Flight Controller
      ↓ (Serial/UDP)
MAVLink Worker Thread
      ↓ (Queue)
Controller (Message Router)
      ↓ (Signals)
UI Components (HUD, Map, Panels)
```

---

## Code Structure

### File Organization

```
ASRA_GCS_with_map/
├── asra_gcs_main.py          # Application entry point
├── gcs_ui.py                 # Main UI layout & widgets
├── controller.py             # MVC controller
├── mavlink_worker.py         # MAVLink communication thread
├── professional_gcs_map.py   # Map widget with tile management
├── hud_widget_reference_style.py  # HUD display
├── config.py                 # Configuration management
├── logger.py                 # Telemetry logging
├── logging_config.py         # Logging configuration
├── performance_monitor.py    # Performance tracking
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
├── CHANGELOG.md             # Version history
├── .gitignore               # Git exclusions
├── cache/                   # Map tile cache (SQLite)
├── logs/                    # Application logs
├── resources/               # Icons, images
└── docs/                    # Documentation
    ├── USER_MANUAL.md
    ├── DEVELOPER_GUIDE.md
    └── DEVELOPMENT_JOURNEY.md
```

### Module Responsibilities

| Module | Purpose | Key Classes/Functions |
|--------|---------|----------------------|
| `asra_gcs_main.py` | Application bootstrap | `main()` |
| `gcs_ui.py` | UI layout and widgets | `ASRAGCS_UI` |
| `controller.py` | Business logic, message routing | `Controller` |
| `mavlink_worker.py` | MAVLink protocol handling | `MavlinkWorker` |
| `professional_gcs_map.py` | Map rendering | `ProfessionalGCSMap`, `TileDownloadManager` |
| `hud_widget_reference_style.py` | HUD rendering | `ReferenceStyleHUDWidget` |
| `config.py` | Configuration management | `Config`, `MapProvider` |

---

## Key Components

### 1. MAVLink Worker (`mavlink_worker.py`)

**Purpose**: Manages MAVLink communication in a separate thread

**Key Methods**:
```python
class MavlinkWorker(threading.Thread):
    def configure(self, device, baud)      # Set connection parameters
    def connect(self)                       # Establish connection
    def disconnect(self)                    # Close connection
    def arm_disarm(self)                   # Toggle armed state
    def set_mode(self, mode_id)            # Change flight mode
    def get_updates(self)                  # Retrieve telemetry updates (queue)
    def run(self)                          # Main thread loop
    def _process_message(self, msg)        # Parse MAVLink messages
```

**Threading**:
- Runs as daemon thread
- Uses `threading.Lock()` for thread-safe operations
- Queue-based communication with main thread

**Message Processing**:
```python
# Example: Processing ATTITUDE message
elif msg_type == 'ATTITUDE':
    self._update_queue.put(('attitude', {
        'roll': msg.roll,
        'pitch': msg.pitch,
        'yaw': msg.yaw
    }))
```

### 2. Controller (`controller.py`)

**Purpose**: Routes messages and handles user actions

**Key Methods**:
```python
class Controller:
    def __init__(self, ui, worker)         # Initialize with UI and worker
    def update_ui(self)                    # Poll worker queue, update UI
    def on_connect(self)                   # Handle connect button
    def on_arm_disarm(self)                # Handle arm/disarm button
    def on_set_mode(self)                  # Handle mode change
```

**Update Loop**:
- Runs via `QTimer` at 100ms intervals (configurable)
- Polls MAVLink worker's update queue
- Dispatches updates to UI components

### 3. Professional GCS Map (`professional_gcs_map.py`)

**Purpose**: High-performance map widget with tile caching

**Key Classes**:

```python
class TileDownloadManager(QThread):
    """Background tile downloader"""
    def request_tile(provider, z, x, y)    # Request tile download
    def run(self)                          # Download loop
    
class PersistentTileCache:
    """SQLite-based tile storage"""
    def get_tile(provider, z, x, y)        # Retrieve cached tile
    def store_tile(provider, z, x, y, data) # Save tile to cache
    
class ProfessionalGCSMap(QWidget):
    """Main map widget"""
    def update_uav_position(lat, lon, heading)  # Update drone marker
    def paintEvent(event)                  # Render map
    def wheelEvent(event)                  # Zoom via mouse wheel
    def mousePressEvent(event)             # Pan via mouse drag
```

**Tile Coordinate System**:
```python
# Web Mercator projection
def _deg2tile(lat, lon, zoom):
    """Convert geographic coordinates to tile coordinates"""
    lat_rad = math.radians(lat)
    n = 2.0 ** zoom
    x = int((lon + 180.0) / 360.0 * n)
    y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (x, y)
```

### 4. HUD Widget (`hud_widget_reference_style.py`)

**Purpose**: Artificial horizon display

**Rendering Pipeline**:
1. **Background**: Sky (blue) and ground (brown)
2. **Pitch Ladder**: Lines at 10° intervals
3. **Roll Indicator**: Arc with degree markings
4. **Heading Tape**: Compass strip
5. **Speed/Altitude Tapes**: Vertical tape displays
6. **Status Indicators**: Top corners

**Custom Painting**:
```python
def paintEvent(self, event):
    painter = QPainter(self)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # Apply roll transformation
    painter.save()
    painter.translate(center_x, center_y)
    painter.rotate(-math.degrees(self.roll))
    
    # Draw pitch ladder
    self._draw_pitch_ladder(painter, pitch_pixels)
    
    painter.restore()
    # ... more drawing
```

### 5. Configuration System (`config.py`)

**Purpose**: Centralized configuration with JSON persistence

**Usage**:
```python
from config import config

# Get value
zoom = config.get("map", "default_zoom")  # Returns 12

# Set value
config.set("map", "default_zoom", 15)  # Auto-saves to config.json

# Validate configuration
issues = config.validate_config()  # Returns list of problems
```

**Config File Structure**:
```json
{
  "app": {...},
  "ui": {...},
  "map": {...},
  "mavlink": {...},
  "performance": {...}
}
```

---

## Build & Deployment

### Building Windows Executable

**Using PyInstaller**:

1. **Create spec file** (`asra_gcs.spec`):
```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['asra_gcs_main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources', 'resources'),
        ('config.json', '.'),
    ],
    hiddenimports=['pymavlink', 'PIL'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pdb = PDB(a)
exe = EXE(
    pdb,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ASRA_GCS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/logo.ico',  # Convert PNG to ICO
)
```

2. **Build**:
```bash
pyinstaller asra_gcs.spec
```

3. **Output**: `dist/ASRA_GCS.exe`

### Creating Windows Installer

**Using Inno Setup**:

1. **Install Inno Setup**: https://jrsoftware.org/isdl.php

2. **Create installer script** (`installer.iss`):
```iss
[Setup]
AppName=ASRA Ground Control Station
AppVersion=1.0.0
DefaultDirName={autopf}\ASRA_GCS
DefaultGroupName=ASRA GCS
OutputDir=dist
OutputBaseFilename=ASRA_GCS_Setup_v1.0
Compression=lzma2
SolidCompression=yes

[Files]
Source: "dist\ASRA_GCS.exe"; DestDir: "{app}"
Source: "resources\*"; DestDir: "{app}\resources"; Flags: recursesubdirs

[Icons]
Name: "{group}\ASRA GCS"; Filename: "{app}\ASRA_GCS.exe"
Name: "{autodesktop}\ASRA GCS"; Filename: "{app}\ASRA_GCS.exe"

[Run]
Filename: "{app}\ASRA_GCS.exe"; Description: "Launch ASRA GCS"; Flags: postinstall nowait skipifsilent
```

3. **Compile**: Open `installer.iss` in Inno Setup Compiler

---

## Contributing Guidelines

### Code Style

- **PEP 8** compliance (use `black` for formatting)
- **Type hints** encouraged for new code
- **Docstrings** for all classes and public methods (Google style)

**Example**:
```python
def update_uav_position(self, lat: float, lon: float, heading: float = 0) -> None:
    """Update UAV marker position on map.
    
    Args:
        lat: Latitude in decimal degrees
        lon: Longitude in decimal degrees  
        heading: Heading in degrees (0-360), default 0
        
    Returns:
        None
    """
    # Implementation...
```

### Git Workflow

1. **Fork** repository on GitHub
2. **Clone** your fork: `git clone https://github.com/YOUR_USERNAME/ASRA-GCS.git`
3. **Create branch**: `git checkout -b feature/my-feature`
4. **Make changes** and commit: `git commit -m "Add: my feature"`
5. **Push**: `git push origin feature/my-feature`
6. **Open Pull Request** on GitHub

### Commit Message Format

```
Type: Short description (50 chars max)

Optional longer description explaining:
- What changed
- Why it changed
- Any breaking changes

Fixes #123 (if applicable)
```

**Types**: `Add`, `Fix`, `Update`, `Remove`, `Refactor`, `Docs`, `Test`

### Testing Before PR

- Run application and verify it works
- Test affected functionality
- Check for console errors
- Run linters: `black .`, `flake8 .`

---

## Testing

### Manual Testing

**Basic Functionality**:
1. Launch application
2. Connect to SITL or real drone
3. Verify HUD updates
4. Verify map tracking
5. Test arm/disarm
6. Test mode changes

**Performance Testing**:
- Monitor CPU/memory usage
- Check frame rate (target: 30-60 FPS)
- Verify smooth map panning/zooming

### Automated Testing (Future)

**Unit Tests**:
```python
# tests/test_config.py
import pytest
from config import Config

def test_config_load():
    config = Config("test_config.json")
    assert config.get("app", "name") == "ASRA Ground Control Station"

def test_config_validation():
    config = Config()
    issues = config.validate_config()
    assert len(issues) == 0
```

**Run**: `pytest tests/`

### SITL Testing (Software In The Loop)

**Setup ArduCopter SITL**:
```bash
# Install SITL
git clone https://github.com/ArduPilot/ardupilot.git
cd ardupilot/ArduCopter
sim_vehicle.py --console --map

# Connect ASRA GCS to SITL
# Use UDP connection: udp:127.0.0.1:14550
```

---

## Performance Optimization

### Profiling

**UI Performance**:
```python
import time

def paintEvent(self, event):
    start = time.perf_counter()
    # ... rendering code ...
    duration = (time.perf_counter() - start) * 1000
    if duration > 16:  # > 60 FPS
        print(f"WARNING: Frame took {duration:.1f}ms")
```

**Memory Profiling**:
```python
import psutil
process = psutil.Process()
print(f"Memory: {process.memory_info().rss / 1024 / 1024:.1f} MB")
```

### Optimization Tips

**Map Rendering**:
- Use `setUpdatesEnabled(False)` during batch updates
- Implement dirty region tracking
- Cache rendered tiles in QPixmapCache
- Use `QPainter.setRenderHint(QPainter.SmoothPixmapTransform, False)` for faster rendering

**Telemetry Updates**:
- Throttle high-frequency updates (e.g. ATTITUDE at 10Hz max in UI)
- Batch UI updates in single `paintEvent()`
- Use `QTimer.singleShot()` for debouncing

**Memory Management**:
- Limit tile cache size (config: `max_cache_tiles`)
- Clear old flight path points (keep last 1000)
- Use object pooling for frequent allocations

---

## Development Roadmap

### v1.0 (Current)
- ✅ Single drone support
- ✅ Professional HUD
- ✅ Satellite maps with caching
- ✅ Basic telemetry and control

### v2.0 (Planned)
- 🔜 Multi-drone support (up to 2 drones)
- 🔜 Flexible UI layouts
- 🔜 Flight data logging
- 🔜 Ubuntu packaging

### Future
- Mission planning (waypoint editor)
- Geofencing
- Video streaming
- Data replay

---

## Useful Resources

**ArduPilot Documentation**:
- [MAVLink Protocol](https://mavlink.io/en/)
- [ArduPilot Dev Docs](https://ardupilot.org/dev/)
- [PyMavlink Guide](https://mavlink.io/en/mavgen_python/)

**PyQt5 Documentation**:
- [Official Docs](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- [Qt5 Reference](https://doc.qt.io/qt-5/)

**Map Tile Providers**:
- [Esri World Imagery](https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer)
- [OpenStreetMap](https://wiki.openstreetmap.org/wiki/Tile_servers)

---

## Contact & Support

**Issues**: [GitHub Issues](https://github.com/Zuhaib77/ASRA-GCS/issues)  
**Discussions**: [GitHub Discussions](https://github.com/Zuhaib77/ASRA-GCS/discussions)  
**Developer**: [@Zuhaib77](https://github.com/Zuhaib77)

---

**Version**: 1.0.0 | **Last Updated**: January 5, 2026
