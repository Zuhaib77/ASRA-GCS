# Building Installers for ASRA GCS v2.0

This guide explains how to create installers for both Windows and Ubuntu platforms.

---

## Windows Installer

### Prerequisites
- Python 3.8+
- PyInstaller: `pip install pyinstaller`
- Inno Setup: Download from https://jrsoftware.org/isdl.php

### Step 1: Build Executable

```powershell
# Clean previous builds
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue

# Build with PyInstaller
pyinstaller --clean ASRA_GCS.spec

# Verify executable
.\dist\ASRA_GCS_v2.0.exe
```

**Expected output**: `dist\ASRA_GCS_v2.0.exe` (~80-120 MB)

### Step 2: Create Installer with Inno Setup

1. Open Inno Setup Compiler
2. File → Open → Select `installer.iss`
3. Build → Compile
4. Installer created in `Output\ASRA_GCS_v2.0_Setup.exe`

**Expected output**: `Output\ASRA_GCS_v2.0_Setup.exe` (~85-130 MB)

### Step 3: Test Installer

```powershell
# Run installer
.\Output\ASRA_GCS_v2.0_Setup.exe

# Install to test directory
# Launch application
# Verify all features work
```

---

## Ubuntu 22.04+ Installer (.deb)

### Prerequisites
- Ubuntu 22.04 or newer
- dpkg-deb (pre-installed)
- Python 3.8+

### Step 1: Prepare Build Environment

```bash
# Install build tools
sudo apt update
sudo apt install dpkg-dev python3-dev python3-pip

# Install Python dependencies
pip3 install pyqt5 pymavlink pyserial Pillow psutil
```

### Step 2: Build .deb Package

```bash
# Make script executable
chmod +x build-ubuntu-installer.sh

# Run builder script
./build-ubuntu-installer.sh
```

**Expected output**: `asra-gcs_2.0.0_amd64.deb` (~5-10 MB source package)

### Step 3: Test Installation

```bash
# Install package
sudo apt install ./asra-gcs_2.0.0_amd64.deb

# Launch from terminal
asra-gcs

# Or launch from Applications menu
# Search for "ASRA GCS"
```

### Step 4: Verify Installation

```bash
# Check installation location
ls -la /opt/asra-gcs/

# Check launcher
which asra-gcs

# Check desktop entry
ls -la /usr/share/applications/asra-gcs.desktop

# Test launch
asra-gcs
```

---

## Quick Build Commands

### Windows (PowerShell)
```powershell
# One-command build
pyinstaller --clean ASRA_GCS.spec ; Write-Host "✓ Executable built!" -ForegroundColor Green

# Build + Create Installer (requires Inno Setup in PATH)
pyinstaller --clean ASRA_GCS.spec
iscc installer.iss
```

### Ubuntu (Bash)
```bash
# One-command build
chmod +x build-ubuntu-installer.sh && ./build-ubuntu-installer.sh
```

---

## File Sizes

| Platform | Type | Approximate Size |
|----------|------|------------------|
| Windows | Executable (.exe) | 80-120 MB |
| Windows | Installer (.exe) | 85-130 MB |
| Ubuntu | Source Package (.deb) | 5-10 MB |
| Ubuntu | Installed Size | ~50 MB |

---

## Distribution

### Windows Files to Distribute
- `Output/ASRA_GCS_v2.0_Setup.exe` - Installer (Recommended)
- `dist/ASRA_GCS_v2.0.exe` - Portable executable (Alternative)

### Ubuntu Files to Distribute
- `asra-gcs_2.0.0_amd64.deb` - Debian package

---

## Troubleshooting

### Windows

**Error: "Module not found"**
- Solution: Add missing module to `hiddenimports` in `ASRA_GCS.spec`

**Error: "Build failed"**
- Solution: Run `pip install pyinstaller --upgrade`
- Clean build: `Remove-Item -Recurse build, dist`

**Installer won't launch app**
- Solution: Check icon path in `installer.iss`
- Verify executable name matches

### Ubuntu

**Error: "dpkg-deb: error"**
- Solution: Check file permissions in build directory
- Ensure control file has correct format

**Dependencies not installing**
- Solution: Install manually: `pip3 install pymavlink pyserial`
- Or use apt: `sudo apt install python3-pymavlink python3-serial`

**Desktop entry not showing**
- Solution: Run `update-desktop-database`
- Check icon exists in `/usr/share/pixmaps/`

---

## Automated Build Scripts

### Windows Complete Build
```powershell
# build-windows.ps1
Remove-Item -Recurse -Force build, dist, Output -ErrorAction SilentlyContinue
pyinstaller --clean ASRA_GCS.spec
if (Test-Path "dist\ASRA_GCS_v2.0.exe") {
    iscc installer.iss
    Write-Host "✓ Build complete!" -ForegroundColor Green
    Write-Host "Installer: Output\ASRA_GCS_v2.0_Setup.exe"
}
```

### Ubuntu Complete Build
See `build-ubuntu-installer.sh` (already created)

---

## Release Checklist

- [ ] Clean build directories
- [ ] Update version numbers
- [ ] Test executable locally
- [ ] Create installer
- [ ] Test installer on clean system
- [ ] Verify all features work
- [ ] Create release on GitHub
- [ ] Upload installers
- [ ] Update download links

---

## Notes

- Windows installer requires admin rights
- Ubuntu package auto-installs Python dependencies
- Both installers are ~100MB due to Python runtime inclusion
- Source distribution alternative available (pip install)
