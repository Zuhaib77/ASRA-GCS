# Changelog

All notable changes to ASRA Ground Control Station will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned for v2.0
- Multi-drone support (up to 2 simultaneous connections)
- Flexible UI layouts (tabs/grid/master-detail)
- Advanced map behaviors with multi-drone tracking
- Manual flight data logging (CSV/JSON/tlog formats)
- Drone naming system (COM port/System ID/Custom names)
- Ubuntu support and packaging

---

## [1.0.0] - 2026-01-05

### Added
- Professional Ground Control Station for ArduPilot drones
- Real-time telemetry display with HUD widget
  - Artificial horizon with pitch ladder and roll indicator
  - Heading tape with compass
  - Flight instruments (airspeed, altitude, vertical speed)
  - Status indicators (connection, armed, GPS, battery)
- Interactive satellite map display
  - Multiple free map providers (Esri Satellite, OpenStreetMap, CartoDB, Stamen)
  - Offline tile caching with SQLite database
  - Real-time UAV position tracking
  - Flight path visualization
  - Home position marker
- Vehicle control commands
  - Arm/Disarm with safety checks
  - Flight mode changes (Stabilize, Alt Hold, Loiter, Auto, Guided, RTL, Land)
  - Mission start/abort commands
  - Force arm (with confirmation dialog)
- Message console
  - Real-time flight controller STATUSTEXT messages
  - Color-coded messages (errors, warnings, info)
  - Smart troubleshooting suggestions
- Configuration management
  - JSON-based configuration system
  - Multiple map providers support
  - Performance optimization settings
  - Persistent user preferences
- Dark theme UI with professional styling
- Comprehensive logging system
  - Separate logs for application, MAVLink, errors, performance
  - Rotating log files with size limits
- Performance monitoring
  - UI update rate tracking
  - Tile download performance metrics
  - Memory usage monitoring

### Changed
- Reorganized codebase into professional structure
- Optimized map rendering for 60 FPS performance
- Improved MAVLink communication reliability
- Enhanced error handling and recovery

### Technical Details
- **Python**: 3.7+
- **GUI Framework**: PyQt5
- **Communication**: PyMavlink
- **Platforms**: Windows (primary), Linux (planned v2.0)

---

## Development Milestones

### Pre-v1.0 Development
- Initial prototype with basic MAVLink communication
- Basic HUD widget implementation
- Map integration with free tile providers
- SQLite-based tile caching
- Performance optimizations
- Message routing and telemetry display

---

## Notes

- This is the first production release of ASRA GCS
- Multi-drone support is planned for v2.0
- Community feedback and contributions welcome

---

**Legend**:
- `Added` - New features
- `Changed` - Changes to existing functionality
- `Deprecated` - Soon-to-be removed features
- `Removed` - Removed features
- `Fixed` - Bug fixes
- `Security` - Vulnerability fixes
