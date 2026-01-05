# ASRA GCS - User Manual

> **Version**: 1.0.0  
> **Last Updated**: January 5, 2026  
> **Platform**: Windows, Linux (Ubuntu)

---

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [User Interface](#user-interface)
5. [Connecting to Your Drone](#connecting-to-your-drone)
6. [Flight Operations](#flight-operations)
7. [Map Features](#map-features)
8. [Configuration](#configuration)
9. [Troubleshooting](#troubleshooting)
10. [FAQ](#faq)
11. [Safety Guidelines](#safety-guidelines)

---

## Introduction

ASRA Ground Control Station (GCS) is a professional-grade ground control software for ArduPilot-based drones. It provides real-time telemetry monitoring, flight control, and mission planning capabilities through an intuitive interface.

### Key Features
- **Real-time HUD** - Artificial horizon with flight instruments
- **Satellite Maps** - FREE Esri World Imagery with offline caching
- **Flight Control** - Arm, disarm, mode changes, mission commands
- **Telemetry Display** - Live data from your drone
- **Message Console** - Flight controller status and diagnostics

### System Requirements
- **OS**: Windows 10/11 or Ubuntu 20.04+
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 500MB for application + cache space
- **Display**: 1280x720 minimum resolution
- **Python**: 3.7+ (for source installation only)

---

## Installation

### Windows Installation

**Method 1: Installer (Recommended)**

1. Download `ASRA_GCS_Setup_v1.0.exe` from [GitHub Releases](https://github.com/Zuhaib77/ASRA-GCS/releases)
2. Double-click the installer
3. Follow the installation wizard
4. Launch from Start Menu → ASRA GCS

**Method 2: Standalone Executable**

1. Download `ASRA_GCS_v1.0.exe` from releases
2. Place in a folder of your choice
3. Double-click to run (no installation needed)

### Linux Installation

```bash
# Install dependencies
sudo apt update
sudo apt install python3 python3-pip python3-pyqt5

# Clone or download release
git clone https://github.com/Zuhaib77/ASRA-GCS.git
cd ASRA-GCS

# Install Python dependencies
pip3 install -r requirements.txt

# Run
python3 asra_gcs_main.py
```

---

## Getting Started

### First Launch

1. **Launch ASRA GCS**
   - Windows: Start Menu → ASRA GCS
   - Linux: `python3 asra_gcs_main.py`

2. **Initial Setup**
   - Application creates configuration files automatically
   - Default settings are optimized for most users
   - No additional configuration required

3. **Interface Overview**
   - **Left**: Artificial Horizon HUD
   - **Center**: Satellite Map
   - **Right**: Telemetry panels
   - **Bottom**: Connection controls and messages

---

## User Interface

### HUD (Heads-Up Display)

The HUD provides critical flight information at a glance:

**Components:**
- **Artificial Horizon** - Shows aircraft attitude (pitch and roll)
- **Pitch Ladder** - Vertical reference lines at 10° intervals
- **Roll Indicator** - Arc with degree markings
- **Heading Tape** - Compass strip showing current heading
- **Speed Tape** - Airspeed indicator (left side)
- **Altitude Tape** - Current altitude (right side)
- **Status Indicators**:
  - 🟢 **CONNECTED** / 🔴 **DISCONNECTED**
  - 🔴 **ARMED** / ⚪ **DISARMED**
  - GPS fix type and satellite count
  - Battery percentage with color coding

**Reading the HUD:**
- **Level Flight**: Horizon line horizontal, zero pitch/roll
- **Climbing**: Horizon line below center
- **Descending**: Horizon line above center
- **Banking**: Horizon line tilted

### Map Display

Interactive satellite map with drone tracking:

**Features:**
- **Pan**: Click and drag
- **Zoom**: Mouse scroll wheel or +/- buttons
- **UAV Marker**: Real-time position with heading indicator
- **Home Marker**: Launch/RTL point
- **Flight Path**: Historical trail (red line)

**Map Controls:**
- Right-click for context menu
- Double-click to center on location
- Map provider selection (top-right dropdown)

### Telemetry Panels

**Attitude Panel:**
- Roll: ±180°
- Pitch: ±90°
- Yaw: 0-360°
- Flight Mode: Current mode name

**GPS Panel:**
- Fix Type: No GPS, 2D, 3D, DGPS, RTK
- Satellites: Number tracked
- HDOP/VDOP: Position dilution (lower is better)
- Lat/Lon: Decimal degrees

**System Status:**
- Voltage: Battery voltage (V)
- Current: Current draw (A)
- Battery: Remaining capacity (%)

### Vehicle Actions

**Available Commands:**
- **Arm/Disarm**: Enable/disable motors
- **Force Arm**: Bypass pre-arm checks (⚠️ use with caution)
- **Set Mode**: Change flight mode
- **Start Mission**: Begin autonomous mission
- **Abort Landing**: Return to launch (RTL)

### Messages Console

Displays real-time messages from flight controller:

**Message Types:**
- 🔴 **Errors**: Critical issues requiring attention
- 🟠 **Warnings**: Non-critical alerts
- 🔵 **Info**: Status updates

**Smart Suggestions:**
- Yellow text appears with troubleshooting hints
- Example: "Need 3D Fix" → "Suggestion: Ensure clear sky view for GPS lock"

---

## Connecting to Your Drone

### Serial (USB) Connection

1. **Connect Hardware**
   - Plug USB cable from flight controller to computer
   - Wait for drivers to install (Windows)

2. **Select Port**
   - Click **Refresh** button
   - Select COM port from dropdown (e.g., "COM3 - USB Serial Device")
   - Common ports: COM3, COM4 (Windows) | /dev/ttyUSB0, /dev/ttyACM0 (Linux)

3. **Select Baud Rate**
   - Default: **57600** (most common)
   - Try 115200 if 57600 doesn't work

4. **Connect**
   - Click **Connect** button
   - Wait for "Connected" message
   - HUD should show "CONNECTED" status

### UDP/TCP Connection

For wireless telemetry or SITL:

1. **Configure Connection String** (in code or future UI)
   - UDP: `udp:127.0.0.1:14550` (SITL)
   - TCP: `tcp:192.168.1.100:5760` (telemetry module)

2. **Connect** as normal

### Connection Troubleshooting

**"No ports detected"**
- Check USB cable connection
- Try different USB port
- Restart computer
- Install FTDI/CH340 drivers if needed

**"Connection failed"**
- Verify correct COM port
- Try different baud rate (115200)
- Close other GCS software (Mission Planner, QGC)
- Check flight controller is powered

**"Connected but no telemetry"**
- Wait 10-15 seconds for initial sync
- Check Messages panel for errors
- Verify MAVLink stream rates on flight controller

---

## Flight Operations

### Pre-Flight Checks

Before arming, verify:
1. ✅ GPS has 3D fix (6+ satellites)
2. ✅ Battery voltage adequate
3. ✅ No PreArm errors in Messages
4. ✅ Correct flight mode selected
5. ✅ Home position set on map

### Arming the Vehicle

**Normal Arm:**
1. Ensure all pre-arm checks pass (watch Messages panel)
2. Click **Arm/Disarm** button
3. Wait for confirmation message
4. HUD shows **ARMED** status

**Force Arm (Emergency Only):**
1. Click **Force Arm**
2. **Confirm** dialog (⚠️ bypasses safety checks)
3. Use only if you understand pre-arm failures

### Changing Flight Mode

1. Select mode from dropdown:
   - **Stabilize**: Manual with self-leveling
   - **Alt Hold**: Hold altitude, manual horizontal
   - **Loiter**: Hold position and altitude
   - **Auto**: Follow mission waypoints
   - **Guided**: External command control
   - **RTL**: Return to launch
   - **Land**: Automatic landing

2. Click **Set Mode**
3. Wait for confirmation in Messages panel
4. HUD shows new mode name

### In-Flight Monitoring

**Watch for:**
- Stable GPS (no "GPS Glitch" messages)
- Battery level (minimum 20% for RTL)
- Altitude and speed (within safe limits)
- Flight mode (correct for current operation)

**Warning Signs:**
- ⚠️ "EKF variance" warnings
- ⚠️ "GPS Glitch" messages
- ⚠️ Battery below 30%
- ⚠️ Unexpected flight mode changes

### Emergency Procedures

**Lost Control Link:**
- Vehicle should activate failsafe (RTL or LAND)
- Monitor map for vehicle returning home

**Low Battery:**
- Initiate RTL immediately (click RTL mode)
- Or manually land if close

**GPS Failure:**
- Switch to **Stabilize** or **Alt Hold**
- Manually fly to safe landing area
- Do NOT use Auto, Loiter, or RTL

**Uncommanded Movement:**
- Switch to **Stabilize**
- Land immediately
- Investigate compass or GPS issues after landing

---

## Map Features

### Map Providers

Switch between providers via dropdown:

- **Esri World Imagery**: High-quality satellite (default)
- **OpenStreetMap**: Street map with labels
- **CartoDB Positron**: Clean, minimal basemap
- **Stamen Terrain**: Topographic map

All providers are **FREE** and require no API keys.

### Offline Caching

- Tiles auto-cache as you pan/zoom
- Cache stored in `cache/tiles.db` (SQLite)
- Works offline after tiles downloaded
- Clear cache: Delete `cache/tiles.db` and restart

### Map Overlays

**UAV Marker:**
- Red triangle pointing in heading direction
- Updates in real-time (~5-10 Hz)
- Size scales with zoom level

**Home Marker:**
- Green circular marker
- Set automatically on arm
- Displayed as "H" icon

**Flight Path:**
- Red line showing historical positions
- Limited to last 1000 points
- Clear via: Right-click → "Clear Flight Path"

### Map Interactions

**Pan:** Click and drag  
**Zoom:** Scroll wheel or +/- buttons  
**Center on UAV:** Double-click UAV marker  
**Context Menu:** Right-click on map

Future versions will support:
- Waypoint creation
- Geofence drawing
- Distance/bearing measurements

---

## Configuration

### Configuration File

Location: `config.json` (in application directory)

Auto-created on first run with defaults. Edit manually or wait for GUI settings (v2.0).

### Key Settings

```json
{
  "map": {
    "default_provider": "Esri World Imagery",
    "default_lat": 28.6139,
    "default_lon": 77.2090,
    "default_zoom": 12,
    "max_cache_tiles": 400
  },
  "ui": {
    "theme": "dark",
    "update_rate_ms": 100
  },
  "mavlink": {
    "heartbeat_timeout": 3.0,
    "default_baud": 57600
  }
}
```

**Common Customizations:**
- `default_lat/lon`: Change starting map position
- `theme`: "dark" or "light"
- `default_baud`: Change default baud rate

### Theme Toggle

**Switching Themes:**
1. Edit `config.json`
2. Change `"theme": "dark"` to `"theme": "light"`
3. Restart application

(GUI toggle coming in v2.0)

### Map Position Persistence

Last map position auto-saves and restores on startup.

**Reset Map:**
- Edit `config.json` and change `default_lat/lon/zoom`
- Or delete config file to reset all settings

---

## Troubleshooting

### Application Won't Start

**Windows:**
- Check antivirus isn't blocking
- Run as Administrator
- Reinstall application

**Linux:**
- Check Python version: `python3 --version` (need 3.7+)
- Install missing dependencies: `pip3 install -r requirements.txt`
- Check permissions: `chmod +x asra_gcs_main.py`

### Map Not Loading

**Symptoms:** Blank map or loading tiles endlessly

**Solutions:**
1. Check internet connection (required for first load)
2. Try different map provider
3. Clear tile cache: Delete `cache/tiles.db`
4. Check firewall isn't blocking tile requests

### Telemetry Not Updating

**Symptoms:** HUD frozen, data not changing

**Solutions:**
1. Check connection status (should be green)
2. Disconnect and reconnect
3. Verify flight controller is streaming data
4. Check Messages panel for MAVLink errors

### High CPU/Memory Usage

**Normal Usage:**
- CPU: 10-25%
- Memory: 200-400 MB

**If Higher:**
- Reduce `update_rate_ms` in config (increase value)
- Lower `max_cache_tiles` (reduce to 200)
- Close other applications
- Update graphics drivers

### PreArm Failures

Common messages and solutions:

| Message | Solution |
|---------|----------|
| "Need 3D Fix" | Wait for GPS lock (clear sky view) |
| "Compass variance" | Calibrate compass away from metal |
| "Accelerometer not calibrated" | Calibrate IMU in Mission Planner |
| "RC not calibrated" | Calibrate radio in Mission Planner |
| "Throttle too high" | Lower throttle stick to minimum |
| "Safety switch" | Press safety switch on flight controller |

---

## FAQ

**Q: Can I use ASRA GCS with PX4 firmware?**  
A: Currently optimized for ArduPilot. PX4 may work but is untested.

**Q: Does ASRA GCS support mission planning?**  
A: Not in v1.0. Use Mission Planner or QGC for mission planning. ASRA GCS can execute uploaded missions.

**Q: Can I connect multiple drones?**  
A: Not in v1.0. Multi-drone support planned for v2.0.

**Q: Is internet required?**  
A: Only for initial map tile downloads. Works offline afterward (if tiles cached).

**Q: Can I use my own map tiles?**  
A: Not currently. Custom tile servers may be supported in future.

**Q: How do I report bugs?**  
A: Open issue on [GitHub](https://github.com/Zuhaib77/ASRA-GCS/issues)

**Q: Is ASRA GCS free?**  
A: Yes, and open-source (license TBD).

**Q: Can I contribute to development?**  
A: Yes! See [Developer Guide](DEVELOPER_GUIDE.md)

---

## Safety Guidelines

### General Safety

1. **Always maintain visual line of sight** with your drone
2. **Never rely solely on GCS** - have RC transmitter ready
3. **Monitor battery levels** - land with at least 20% remaining
4. **Respect local regulations** - check airspace restrictions
5. **Test in safe area** before critical missions

### Using GCS Safely

1. **Verify commands** - Double-check mode changes and arm states
2. **Monitor messages** - Watch for warnings and errors
3. **Have backup plan** - Know how to manually fly/land
4. **Don't force arm** unless you fully understand the risks
5. **Keep GCS updated** - Check for software updates regularly

### Emergency Contact

In case of emergency (flyaway, crash, injury):
1. **Land immediately** if possible (RTL or manual)
2. **Kill motors** if crashing (disarm)
3. **Contact authorities** if necessary (lost drone, property damage)
4. **Report incidents** to local aviation authority if required

---

## Support

**Documentation:**
- [GitHub Wiki](https://github.com/Zuhaib77/ASRA-GCS/wiki)
- [Developer Guide](DEVELOPER_GUIDE.md)
- [Development Journey](DEVELOPMENT_JOURNEY.md)

**Community:**
- [GitHub Issues](https://github.com/Zuhaib77/ASRA-GCS/issues) - Bug reports
- [GitHub Discussions](https://github.com/Zuhaib77/ASRA-GCS/discussions) - Q&A

**Developer:**
- GitHub: [@Zuhaib77](https://github.com/Zuhaib77)

---

**Version**: 1.0.0 | **Last Updated**: January 5, 2026
