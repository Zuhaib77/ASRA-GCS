# ASRA Ground Control Station

<div align="center">

![ASRA GCS Logo](resources/logo.png)

**Professional Ground Control Station for ArduPilot Drones**

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/Zuhaib77/ASRA-GCS/releases)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey.svg)](https://github.com/Zuhaib77/ASRA-GCS)
[![License](https://img.shields.io/badge/license-TBD-orange.svg)](LICENSE)

</div>

---

## 🚀 Features

### Real-Time Telemetry & Control
- **Professional HUD** - Artificial horizon with pitch ladder, roll indicator, and flight instruments
- **Satellite Map Display** - FREE Esri World Imagery with offline caching
- **Flight Control** - Arm/disarm, mode changes, mission commands
- **Live Telemetry** - Airspeed, altitude, GPS, battery monitoring
- **Message Console** - Flight controller messages with smart suggestions

### Professional Interface
- **Mission Planner Style** - Familiar layout for drone operators
- **Dark/Light Themes** - Toggle between themes with persistent preferences
- **Responsive Design** - Optimized for various screen sizes
- **Smooth Animations** - 60 FPS rendering for fluid user experience

### Advanced Mapping
- **Multiple Map Providers** - OpenStreetMap, Esri Satellite, CartoDB, Stamen
- **Offline Tile Caching** - SQLite-based cache for offline operation
- **Flight Path Tracking** - Real-time UAV position and historical path
- **Performance Optimized** - Efficient tile loading and rendering

---

## 📦 Installation

### Windows (Recommended)

**Option 1: Installer (Easiest)**
1. Download `ASRA_GCS_Setup_v1.0.exe` from [Releases](https://github.com/Zuhaib77/ASRA-GCS/releases)
2. Run the installer
3. Launch from Start Menu

**Option 2: Standalone Executable**
1. Download `ASRA_GCS_v1.0.exe` from [Releases](https://github.com/Zuhaib77/ASRA-GCS/releases)
2. Run directly (no installation needed)

### From Source

```bash
# Clone repository
git clone https://github.com/Zuhaib77/ASRA-GCS.git
cd ASRA-GCS

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux

# Install dependencies
pip install -r requirements.txt

# Run application
python asra_gcs_main.py
```

---

## 🎯 Quick Start

1. **Launch ASRA GCS**
2. **Select Connection**:
   - Choose COM port from dropdown
   - Select baud rate (default: 57600)
   - Click **Connect**
3. **Monitor Telemetry**:
   - HUD displays attitude and flight data
   - Map shows UAV position in real-time
   - Messages panel shows flight controller status
4. **Control Vehicle**:
   - **Arm/Disarm** - Enable/disable motors
   - **Change Mode** - Select flight mode (Stabilize, Loiter, Auto, RTL, etc.)
   - **Mission Commands** - Start mission, abort landing

---

## 🎨 Features in Detail

### Artificial Horizon HUD
- **Pitch Ladder** - Visual reference for pitch angle
- **Roll Indicator** - Arc display with numeric readout
- **Heading Tape** - Compass heading with cardinal directions
- **Flight Instruments** - Airspeed, altitude, vertical speed
- **Status Indicators** - Connection, armed status, GPS fix, battery level

### Interactive Map
- **Pan & Zoom** - Mouse drag to pan, scroll to zoom
- **UAV Tracking** - Real-time position with heading indicator
- **Home Position** - Launch point marker
- **Flight Path** - Historical trail
- **Right-Click Context Menu** - Quick actions and information

### Flight Controller Messages
- **Color-Coded** - Red for errors, orange for warnings, cyan for info
- **Smart Suggestions** - Automated troubleshooting hints
- **Message Filtering** - Focus on important notifications

---

## ⚙️ Configuration

Configuration file: `config.json` (auto-created on first run)

### Key Settings

```json
{
  "map": {
    "default_provider": "Esri World Imagery",
    "default_lat": 28.6139,
    "default_lon": 77.2090,
    "default_zoom": 12
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

---

## 🛠️ Troubleshooting

### Can't Connect to Vehicle

**Check:**
- ✅ Correct COM port selected
- ✅ Correct baud rate (57600 or 115200)
- ✅ No other software using the port (Mission Planner, QGroundControl)
- ✅ USB cable properly connected
- ✅ Flight controller powered on

### No Telemetry Updates

**Check:**
- ✅ Connection established (check status indicator)
- ✅ MAVLink stream rates configured on flight controller
- ✅ Messages panel for errors

### PreArm Failures

**Common Issues:**
- "Need 3D Fix" → Wait for GPS lock (clear sky view required)
- "Compass variance" → Calibrate compass away from metal objects
- "RC not calibrated" → Calibrate radio in Mission Planner/QGC

---

## 📚 Documentation

- **[User Manual](docs/USER_MANUAL.md)** - Detailed usage guide
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)** - For contributors and developers
- **[Development Journey](docs/DEVELOPMENT_JOURNEY.md)** - Project evolution and learnings
- **[CHANGELOG](CHANGELOG.md)** - Version history

---

## 🚀 Roadmap

### v1.0 (Current)
- ✅ Single drone support
- ✅ Professional HUD and map display
- ✅ Dark/Light theme toggle
- ✅ Windows installer

### v2.0 (Planned)
- 🔜 **Multi-Drone Support** - Control up to 2 drones simultaneously
- 🔜 Flexible layout system (tabs/grid/master-detail)
- 🔜 Advanced map behaviors (follow selected, show all, manual)
- 🔜 Flight data logging (CSV/JSON/tlog)
- 🔜 Ubuntu support

---

## 🤝 Contributing

Contributions welcome! Please read [DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) first.

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📝 License

License TBD - Stay tuned for updates

---

## 🙏 Acknowledgments

- **[PyMavlink](https://github.com/ArduPilot/pymavlink)** - MAVLink protocol implementation
- **[PyQt5](https://www.riverbankcomputing.com/software/pyqt/)** - GUI framework
- **[ArduPilot](https://ardupilot.org/)** - Flight controller firmware
- **[Esri](https://www.esri.com/)** - FREE World Imagery tiles
- **[OpenStreetMap](https://www.openstreetmap.org/)** - FREE map data

---

## 📧 Contact

**Developer**: Zuhaib77  
**GitHub**: [github.com/Zuhaib77](https://github.com/Zuhaib77)  
**Project**: [github.com/Zuhaib77/ASRA-GCS](https://github.com/Zuhaib77/ASRA-GCS)

---

<div align="center">

**Made with ❤️ for the drone community**

</div>
