# Build Instructions for ASRA GCS v2.0

## Prerequisites
- Python 3.8+ installed
- All dependencies from requirements.txt installed
- PyInstaller: `pip install pyinstaller`
- Inno Setup (for installer): https://jrsoftware.org/isdl.php

## Building Executable

### Step 1: Clean Previous Builds
```bash
Remove-Item -Recurse -Force build, dist
```

### Step 2: Build with PyInstaller
```bash
pyinstaller ASRA_GCS.spec
```

This creates:
- `dist/ASRA_GCS_v2.0.exe` - Standalone executable

### Step 3: Test Executable
```bash
.\dist\ASRA_GCS_v2.0.exe
```

Verify:
- Application launches
- UI displays correctly
- Can select COM ports
- Map loads properly

## Creating Installer

### Step 1: Build Executable First
Complete PyInstaller build above

### Step 2: Compile Installer
1. Open `installer.iss` in Inno Setup
2. Click Build > Compile
3. Installer created in `Output/` directory

### Step 3: Test Installer
1. Run `Output/ASRA_GCS_v2.0_Setup.exe`
2. Install to test location
3. Launch from Start Menu
4. Verify all features work

## Quick Build Script

```powershell
# Clean
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue

# Build
pyinstaller ASRA_GCS.spec

# Test
if (Test-Path "dist\ASRA_GCS_v2.0.exe") {
    Write-Host "✓ Build successful!" -ForegroundColor Green
    Write-Host "Executable: dist\ASRA_GCS_v2.0.exe"
} else {
    Write-Host "✗ Build failed!" -ForegroundColor Red
}
```

## Troubleshooting

### Missing modules
Add to `hiddenimports` in ASRA_GCS.spec

### Large file size
- Check `excludes` list
- Use UPX compression
- Remove unnecessary dependencies

### Icon not showing
- Verify icon path in .spec
- Use .ico format for Windows

## File Sizes (Approximate)
- Executable: ~80-120 MB
- Installer: ~85-130 MB

## Distribution
Final files to distribute:
- `Output/ASRA_GCS_v2.0_Setup.exe` - Installer
- `dist/ASRA_GCS_v2.0.exe` - Portable executable
- `docs/USER_MANUAL.md` - User documentation
