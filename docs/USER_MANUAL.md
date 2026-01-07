# ASRA GCS v2.0 - User Manual

## Table of Contents
1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [User Interface](#user-interface)
4. [Connecting Drones](#connecting-drones)
5. [Map Controls](#map-controls)
6. [Troubleshooting](#troubleshooting)

---

## Installation

### System Requirements
- **Operating System**: Windows 10/11 (64-bit)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 500MB free space
- **Graphics**: DirectX 11 compatible
- **Internet**: Required for map tiles (offline cache available)

### Installation Steps

#### Option 1: Installer (Recommended)
1. Download `ASRA_GCS_v2.0_Setup.exe`
2. Double-click to run installer
3. Follow installation wizard
4. Launch from Start Menu or Desktop shortcut

#### Option 2: Python Source
1. Install Python 3.8+ from python.org
2. Clone repository:
   ```
   git clone https://github.com/Zuhaib77/ASRA-GCS.git
   cd ASRA_GCS_with_map
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run application:
   ```
   python asra_gcs_v2.py
   ```

---

## Quick Start

### First Launch
1. **Start Application**: Launch ASRA GCS v2.0
2. **Main Window Opens**: You'll see 3 tabs and a connection sidebar
3. **Connect Drone**: Use left sidebar to configure connection

### 5-Minute Setup
1. **Select Port**: Choose COM port for your drone (e.g., COM3)
2. **Set Baud Rate**: Usually 57600 or 115200
3. **Click Connect**: Connection status will show "Connected"
4. **View Telemetry**: HUD and status cards update automatically
5. **Control Drone**: Use Arm/Disarm and mode change buttons

---

## User Interface

### Layout Overview

```
┌──────────┬─────────────────────────────────────┐
│          │  Tabs: Combined | Drone 1 | Drone 2│
│ SIDEBAR  ├──────────┬──────────┬──────────────┤
│          │  Status  │          │              │
│ Drone 1  │  +HUDs   │   Map    │  Telemetry   │
│ Drone 2  │          │          │   Messages   │
│          │          │  Compare │              │
└──────────┴──────────┴──────────┴──────────────┘
```

### Components

#### Left Sidebar
- **Connection Controls**: Port, baud rate, connect/disconnect
- **System Status**: Shows connected drones count
- **Drone 1 Panel**: Connection for first drone
- **Drone 2 Panel**: Connection for second drone

#### Combined View Tab
- **Left Column**: Status cards + Full HUDs for both drones
- **Center Column**: Global map + Comparison panel
- **Right Column**: Telemetry message log

#### Individual Drone Tabs
- **Large HUD**: Primary flight display
- **Telemetry Panels**: Detailed sensor data
- **Control Buttons**: Arm, Disarm, Mode changes

### Status Card Elements
- **Drone Name**: Color-coded indicator
- **Armed Status**: ARMED (green) or DISARMED (gray)
- **Quick Stats**: Battery, Signal, Satellites, Distance
- **Flight Data**: Altitude, Speed, Heading
- **Mode Display**: Current flight mode
- **Arm Button**: Quick arm/disarm control

### HUD Display
- **Artificial Horizon**: Pitch and roll indicators
- **Heading Compass**: Top center
- **Altitude**: Right side (MSL and AGL)
- **Speed**: Left side (air and ground)
- **Climb Rate**: Vertical speed indicator

---

## Connecting Drones

### Connection Process

#### Step 1: Identify COM Port
1. Connect drone to computer via USB/serial
2. Open Device Manager (Windows)
3. Look under "Ports (COM & LPT)"
4. Note COM port number (e.g., COM3)

#### Step 2: Configure Connection
1. In **Connection Sidebar**, find "Drone 1" section
2. Click **Port** dropdown
3. Select your COM port
4. Select **Baud Rate** (check drone documentation, usually 57600 or 115200)

#### Step 3: Connect
1. Click **Connect** button
2. Status changes to "Connecting..."
3. When successful: "● Connected" (green)
4. Telemetry data starts appearing

#### Step 4: Verify Connection
- HUD should show live attitude data
- Status card shows real-time telemetry
- Map displays drone position (if GPS lock)

### Connecting Multiple Drones
1. Connect Drone 1 first (follow steps above)
2. Connect second drone to different COM port  
3. Configure Drone 2 panel with its COM port
4. Click Connect for Drone 2
5. Both drones now visible in Combined View

### Disconnecting
1. Click **Disconnect** button in sidebar
2. Status changes to "● Disconnected" (red)
3. Telemetry stops updating

---

## Map Controls

### Navigation
- **Zoom In**: Scroll wheel up OR click zoom buttons
- **Zoom Out**: Scroll wheel down OR click zoom buttons
- **Pan**: Click and drag map
- **Zoom Range**: 10 (far) to 19 (close)

### Map Features

#### Crosshair
- **Green crosshair** at map center
- Shows targeting/planning point
- Coordinates displayed at bottom left

#### Coordinate Display (Bottom Left)
```
Center: 28.614300°, 77.209000° | Zoom: 15
```
- **Center**: Crosshair position (lat/lon)
- **Zoom**: Current zoom level

#### Map Info (Bottom Right)
```
Provider: Esri World Imagery
Zoom: 15/19
Tiles: 156
```
- **Provider**: Current map tile source
- **Zoom**: Current/Maximum zoom
- **Tiles**: Number of cached tiles

### Drone Markers
- **Drone 1**: Cyan blue marker (#00d4ff)
- **Drone 2**: Purple marker (#a78bfa)
- **Flight Path**: Colored trail showing travel history

### Map Providers
1. **Esri World Imagery** (Default): Satellite view
2. **OpenStreetMap**: Street map
3. **CartoDB Dark**: Dark theme map

To change provider: Right-click map → Select provider

---

## Troubleshooting

### Connection Issues

#### "No ports detected"
**Problem**: No COM ports shown
**Solutions**:
- Check USB cable connection
- Install drone driver (CH340, FTDI, etc.)
- Try different USB port
- Restart computer

#### "Connection timeout"
**Problem**: Can't connect to drone
**Solutions**:
- Verify correct COM port selected
- Check baud rate matches drone (try 57600, then 115200)
- Ensure drone is powered on
- Check MAVLink is enabled on drone
- Try shorter/better USB cable

#### "Disconnected unexpectedly"
**Problem**: Connection drops during operation
**Solutions**:
- Check USB cable (replace if faulty)
- Verify stable power to drone
- Reduce USB cable length
- Update drone firmware
- Check for interference

### Telemetry Issues

#### "No HUD data"
**Problem**: HUD shows 0s or doesn't update
**Solutions**:
- Verify connection is established (green status)
- Check MAVLink stream rate on drone
- Restart application
- Reconnect drone

#### "GPS shows 0,0"
**Problem**: No GPS position
**Solutions**:
- Wait for GPS lock (requires clear sky view)
- Check "Satellites" count (need 6+ for lock)
- Move drone outdoors/near window
- Check GPS module connection

### Map Issues

#### "Map tiles not loading"
**Problem**: Gray tiles or no map
**Solutions**:
- Check internet connection
- Try different map provider
- Clear cache: Delete `cache/` folder
- Restart application
- Check firewall settings

#### "Map is blank/black"
**Problem**: Nothing visible
**Solutions**:
- Zoom out to level 12-14
- Pan to different location
- Switch map provider
- Update graphics drivers

### Performance Issues

#### "Application slow/laggy"
**Problem**: UI updates slowly
**Solutions**:
- Close other applications
- Reduce zoom level
- Clear map cache
- Reduce update rate in config.py
- Upgrade computer RAM

#### "High CPU usage"
**Problem**: Computer fan loud, slow
**Solutions**:
- Disable performance monitoring
- Reduce telemetry update frequency
- Limit map tile downloads
- Close individual drone tabs if not needed

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+1` | Switch to Combined View |
| `Ctrl+2` | Switch to Drone 1 Tab |
| `Ctrl+3` | Switch to Drone 2 Tab |
| `+` | Zoom in map |
| `-` | Zoom out map |
| `R` | Refresh COM ports |
| `Ctrl+Q` | Quit application |

---

## Safety Guidelines

### Before Flight
1. ✅ **Verify Connection**: Green "Connected" status
2. ✅ **Check Telemetry**: HUD showing real data
3. ✅ **GPS Lock**: 6+ satellites
4. ✅ **Battery Level**: >30% recommended
5. ✅ **Flight Mode**: Verify correct mode selected

### During Operation
- ⚠️ **Monitor Battery**: Watch for low voltage warnings
- ⚠️ **Check Signal**: Maintain good RSSI (>40%)
- ⚠️ **Watch Telemetry**: Look for anomalies
- ⚠️ **Have Manual Override**: Be ready to take manual control

### Emergency
- 🚨 **Connection Lost**: Switch to manual control immediately
- 🚨 **Low Battery**: Land immediately
- 🚨 **GPS Loss**: Switch to manual/STABILIZE mode

---

## Advanced Features

### Configuration File
Edit `config.py` to customize:
- Map providers and defaults
- Update rates
- Zoom limits
- Cache settings
- MAVLink parameters

### Log Files
Located in `logs/` directory:
- `asra_gcs_YYYYMMDD.log`: Daily application logs
- Review for debugging and incident analysis

### Map Cache
Located in `cache/` directory:
- Tiles stored for offline use
- Delete folder to clear cache
- Automatically manages size

---

## Support

### Getting Help
- **Documentation**: README.md, V2_WHATS_NEW.md
- **Issues**: GitHub Issues page
- **Updates**: Check GitHub for new versions

### Reporting Bugs
Include:
1. ASRA GCS version (v2.0)
2. Operating system (Windows version)
3. Steps to reproduce
4. Log file (`logs/` directory)
5. Screenshots if applicable

---

## License & Credits

**ASRA GCS v2.0**
- Free and open-source software
- Multi-drone ground control station
- MAVLink protocol support

**Acknowledgments**:
- PyQt5 GUI framework
- pymavlink library
- OpenStreetMap contributors
- Esri World Imagery

---

*Last Updated: January 2026*
*Version: 2.0.0*
