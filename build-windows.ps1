# Windows Installer Builder for ASRA GCS v2.0
# Run this script to build both executable and installer

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "ASRA GCS v2.0 - Windows Build Script" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Clean previous builds
Write-Host "[1/4] Cleaning previous builds..." -ForegroundColor Yellow
Remove-Item -Recurse -Force build, dist, Output -ErrorAction SilentlyContinue
Write-Host "✓ Clean complete" -ForegroundColor Green
Write-Host ""

# Step 2: Build executable with PyInstaller
Write-Host "[2/4] Building executable with PyInstaller..." -ForegroundColor Yellow
pyinstaller --clean ASRA_GCS.spec

if (-not (Test-Path "dist\ASRA_GCS_v2.0.exe")) {
    Write-Host "✗ Build failed!" -ForegroundColor Red
    exit 1
}

$exeSize = (Get-Item "dist\ASRA_GCS_v2.0.exe").Length / 1MB
Write-Host "✓ Executable built: dist\ASRA_GCS_v2.0.exe ($([math]::Round($exeSize, 2)) MB)" -ForegroundColor Green
Write-Host ""

# Step 3: Test executable (optional quick test)
Write-Host "[3/4] Testing executable..." -ForegroundColor Yellow
Write-Host "  Skipping automated test (run manually to verify UI)" -ForegroundColor Gray
Write-Host ""

# Step 4: Create installer with Inno Setup
Write-Host "[4/4] Creating installer with Inno Setup..." -ForegroundColor Yellow

# Check if Inno Setup is installed
$innoPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if (-not (Test-Path $innoPath)) {
    Write-Host "⚠ Inno Setup not found at: $innoPath" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To create installer:" -ForegroundColor Cyan
    Write-Host "1. Download Inno Setup from https://jrsoftware.org/isdl.php" -ForegroundColor Cyan
    Write-Host "2. Install Inno Setup" -ForegroundColor Cyan
    Write-Host "3. Open installer.iss in Inno Setup" -ForegroundColor Cyan
    Write-Host "4. Click Build > Compile" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Or run: & 'C:\Program Files (x86)\Inno Setup 6\ISCC.exe' installer.iss" -ForegroundColor Cyan
} else {
    & $innoPath installer.iss
    
    if (Test-Path "Output\ASRA_GCS_v2.0_Setup.exe") {
        $installerSize = (Get-Item "Output\ASRA_GCS_v2.0_Setup.exe").Length / 1MB
        Write-Host "✓ Installer created: Output\ASRA_GCS_v2.0_Setup.exe ($([math]::Round($installerSize, 2)) MB)" -ForegroundColor Green
    } else {
        Write-Host "✗ Installer creation failed" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Build Summary" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

if (Test-Path "dist\ASRA_GCS_v2.0.exe") {
    Write-Host "✓ Executable:" -ForegroundColor Green -NoNewline
    Write-Host " dist\ASRA_GCS_v2.0.exe"
}

if (Test-Path "Output\ASRA_GCS_v2.0_Setup.exe") {
    Write-Host "✓ Installer:" -ForegroundColor Green -NoNewline
    Write-Host " Output\ASRA_GCS_v2.0_Setup.exe"
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Test the executable: .\dist\ASRA_GCS_v2.0.exe" -ForegroundColor White
Write-Host "2. Test the installer on a clean system" -ForegroundColor White
Write-Host "3. Upload to GitHub release" -ForegroundColor White
Write-Host ""
