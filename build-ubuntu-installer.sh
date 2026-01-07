#!/bin/bash
# Ubuntu/Debian .deb Package Builder for ASRA GCS v2.0
# Run this script on Ubuntu 22.04+ to create .deb package

set -e

APP_NAME="asra-gcs"
APP_VERSION="2.0.0"
PACKAGE_NAME="${APP_NAME}_${APP_VERSION}_amd64"
BUILD_DIR="build-deb"

echo "===================================="
echo "ASRA GCS v2.0 .deb Package Builder"
echo "===================================="
echo ""

# Clean previous build
echo "Cleaning previous builds..."
rm -rf ${BUILD_DIR}
rm -f ${PACKAGE_NAME}.deb

# Create package structure
echo "Creating package structure..."
mkdir -p ${BUILD_DIR}/DEBIAN
mkdir -p ${BUILD_DIR}/opt/${APP_NAME}
mkdir -p ${BUILD_DIR}/usr/share/applications
mkdir -p ${BUILD_DIR}/usr/share/pixmaps
mkdir -p ${BUILD_DIR}/usr/bin

# Copy application files
echo "Copying application files..."
cp -r *.py ${BUILD_DIR}/opt/${APP_NAME}/
cp requirements.txt ${BUILD_DIR}/opt/${APP_NAME}/
cp -r resources ${BUILD_DIR}/opt/${APP_NAME}/
cp -r docs ${BUILD_DIR}/opt/${APP_NAME}/
cp README.md CHANGELOG.md V2_WHATS_NEW.md ${BUILD_DIR}/opt/${APP_NAME}/

# Create launcher script
echo "Creating launcher script..."
cat > ${BUILD_DIR}/usr/bin/${APP_NAME} << 'EOF'
#!/bin/bash
cd /opt/asra-gcs
python3 asra_gcs_v2.py "$@"
EOF
chmod +x ${BUILD_DIR}/usr/bin/${APP_NAME}

# Create desktop entry
echo "Creating desktop entry..."
cat > ${BUILD_DIR}/usr/share/applications/${APP_NAME}.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=ASRA GCS
Comment=Multi-Drone Ground Control Station
Exec=/usr/bin/${APP_NAME}
Icon=${APP_NAME}
Terminal=false
Categories=Science;Education;
Keywords=drone;uav;mavlink;ground-control;
EOF

# Copy icon
if [ -f resources/logo.png ]; then
    cp resources/logo.png ${BUILD_DIR}/usr/share/pixmaps/${APP_NAME}.png
fi

# Create control file
echo "Creating control file..."
cat > ${BUILD_DIR}/DEBIAN/control << EOF
Package: ${APP_NAME}
Version: ${APP_VERSION}
Section: science
Priority: optional
Architecture: amd64
Depends: python3 (>= 3.8), python3-pyqt5, python3-serial, python3-pil
Maintainer: Zuhaib77 <zuhaib@example.com>
Description: ASRA Ground Control Station - Multi-Drone Support
 Professional Ground Control Station for UAV operations with
 multi-drone support, real-time telemetry, MAVLink communication,
 and advanced mapping capabilities.
 .
 Features:
  - Control up to 2 drones simultaneously
  - Professional HUD with artificial horizon
  - Enhanced mapping system with zoom 10-19
  - Status cards and comparison panel
  - Real-time telemetry monitoring
Homepage: https://github.com/Zuhaib77/ASRA-GCS
EOF

# Create postinst script
echo "Creating postinst script..."
cat > ${BUILD_DIR}/DEBIAN/postinst << 'EOF'
#!/bin/bash
set -e

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --user pymavlink pyserial Pillow psutil

# Update desktop database
if command -v update-desktop-database > /dev/null 2>&1; then
    update-desktop-database -q
fi

echo ""
echo "ASRA GCS v2.0 installed successfully!"
echo "Launch from applications menu or run: asra-gcs"
echo ""

exit 0
EOF
chmod +x ${BUILD_DIR}/DEBIAN/postinst

# Create prerm script
echo "Creating prerm script..."
cat > ${BUILD_DIR}/DEBIAN/prerm << 'EOF'
#!/bin/bash
set -e
exit 0
EOF
chmod +x ${BUILD_DIR}/DEBIAN/prerm

# Build the package
echo "Building .deb package..."
dpkg-deb --build --root-owner-group ${BUILD_DIR} ${PACKAGE_NAME}.deb

# Clean up
echo "Cleaning up..."
rm -rf ${BUILD_DIR}

echo ""
echo "===================================="
echo "✓ Package built successfully!"
echo "===================================="
echo "Package: ${PACKAGE_NAME}.deb"
echo "Size: $(du -h ${PACKAGE_NAME}.deb | cut -f1)"
echo ""
echo "Install with: sudo dpkg -i ${PACKAGE_NAME}.deb"
echo "or: sudo apt install ./${PACKAGE_NAME}.deb"
echo ""
