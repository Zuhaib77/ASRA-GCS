# ASRA GCS v2.0 - Multi-Drone Ground Control Station

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/Zuhaib77/ASRA-GCS/releases)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://github.com/Zuhaib77/ASRA-GCS)

Professional Ground Control Station for multi-drone UAV operations with real-time telemetry, MAVLink communication, and advanced mapping capabilities.

![ASRA GCS v2.0](resources/logo.png)

## 🚀 What's New in v2.0

### Major Features
- ✨ **Multi-Drone Support**: Control up to 2 drones simultaneously
- 🎨 **Redesigned UI**: Modern React-inspired interface with sidebar navigation
- 🗺️ **Enhanced Map**: Professional mapping with zoom 10-19, crosshair, and provider info
- 📊 **Status Cards**: Quick-glance drone metrics with color-coded indicators
- 🎯 **Full HUD Displays**: 400x350 HUD on all views with artificial horizon
- 📡 **Comparison Panel**: Side-by-side drone metrics comparison
- 🔗 **Centralized Connection**: Unified sidebar for all drone connections

### UI Layout
```
┌──────────┬─────────────────────────────────────┐
│          │  Tabs: Combined | Drone 1 | Drone 2│
│ SIDEBAR  ├──────────┬──────────┬──────────────┤
│          │  Status  │          │              │
│ Connect  │  +HUDs   │   Map    │  Telemetry   │
│ Drones   │          │          │   Messages   │
│          │          │  Compare │              │
└──────────┴──────────┴──────────┴──────────────┘
```

## 📥 Installation

### Option 1: Installer (Recommended)
1. Download the latest installer from [Releases](https://github.com/Zuhaib77/ASRA-GCS/releases)
2. Run `ASRA_GCS_v2.0_Setup.exe`
3. Follow the installation wizard
4. Launch from Start Menu

### Option 2: Run from Source
```bash
# Clone repository
git clone https://github.com/Zuhaib77/ASRA-GCS.git
cd ASRA-GCS

# Install dependencies
pip install -r requirements.txt

# Run application
python asra_gcs_v2.py
```

## 🎮 Quick Start

1. **Launch ASRA GCS v2.0**
2. **Connect Drone**:
   - Select COM port in left sidebar
   - Choose baud rate (57600 or 115200)
   - Click "Connect"
3. **Monitor Telemetry**: View live data on HUD and status cards
4. **Control Drone**: Use Arm/Disarm and mode change buttons
5. **Track on Map**: See real-time position and flight path

## 🔥 Key Features

### Multi-Drone Operations
- Simultaneous control of 2 drones
- Independent telemetry streams
- Color-coded identification (Cyan #00d4ff, Purple #a78bfa)
- Unified and individual drone views

### Professional HUD
- Artificial horizon with pitch/roll
- Heading compass
- Altitude (MSL & AGL)
- Speed (air & ground)
- Climb rate indicator

### Advanced Mapping
- **Multiple Providers**: Esri Satellite, OpenStreetMap, CartoDB
- **Zoom Levels**: 10-19 for detailed mission planning
- **Crosshair**: Center targeting point
- **Coordinates**: Real-time lat/lon display
- **Flight Paths**: Historical trail visualization
- **Offline Cache**: Tile caching for disconnected ops

### Status Cards
Quick metrics at a glance:
- Armed/Disarmed status
- Battery level & voltage
- Signal strength (RSSI)
- GPS satellites
- Distance to home
- Altitude, Speed, Heading
- Flight mode

### Telemetry Monitoring
- Real-time sensor data
- MAVLink message log
- Attitude (roll, pitch, yaw)
- GPS position & fix
- Battery status
- System health

## 📋 System Requirements

- **OS**: Windows 10/11 (64-bit)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 500MB free space
- **Graphics**: DirectX 11 compatible
- **Internet**: Required for map tiles (offline cache available)

## 🛠️ Technology Stack

- **GUI Framework**: PyQt5
- **MAVLink**: pymavlink
- **Serial Communication**: pyserial
- **Mapping**: Custom tile downloader with caching
- **Configuration**: JSON-based config management
- **Logging**: Advanced logging with rotation

## 📖 Documentation

- **User Manual**: [docs/USER_MANUAL.md](docs/USER_MANUAL.md) - Complete usage guide
- **Build Guide**: [docs/BUILD.md](docs/BUILD.md) - How to build from source
- **What's New**: [V2_WHATS_NEW.md](V2_WHATS_NEW.md) - v2.0 changelog
- **Changelog**: [CHANGELOG.md](CHANGELOG.md) - Version history

## 🎯 Use Cases

- **Research & Development**: UAV testing and development
- **Education**: Student projects and training
- **Hobby**: RC aircraft and drone enthusiasts
- **Commercial**: Inspection, mapping, surveillance
- **Multi-Drone**: Swarm operations and coordinated missions

## 🔧 Configuration

Edit `config.py` to customize:
- Map providers and tile sources
- Update rates and performance
- Zoom limits
- Cache settings
- MAVLink stream rates
- UI preferences

## 🐛 Troubleshooting

### Connection Issues
- Check COM port selection
- Verify baud rate (usually 57600 or 115200)
- Ensure MAVLink is enabled on drone
- Try different USB cable/port

### Map Not Loading
- Check internet connection
- Try different map provider
- Clear cache folder
- Verify firewall settings

See [USER_MANUAL.md](docs/USER_MANUAL.md) for detailed troubleshooting.

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **PyQt5** - GUI framework
- **pymavlink** - MAVLink protocol implementation
- **OpenStreetMap** - Map tile contributors
- **Esri** - World Imagery satellite tiles
- **Community** - Testers and contributors

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Zuhaib77/ASRA-GCS/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Zuhaib77/ASRA-GCS/discussions)
- **Documentation**: [docs/](docs/)

## 🗺️ Roadmap

- [ ] Support for 4+ drones
- [ ] Mission planning interface
- [ ] Flight log playback
- [ ] Real-time video streaming
- [ ] Geofencing and no-fly zones
- [ ] Auto-update mechanism
- [ ] Mobile companion app

## 📊 Project Stats

- **Version**: 2.0.0
- **Status**: Production Ready
- **Last Updated**: January 2026
- **Language**: Python
- **Lines of Code**: ~15,000+

---

**Made with ❤️ for the UAV community**

*Star ⭐ this repository if you find it useful!*
