"""
Build script for ASRA GCS Windows executable
Uses PyInstaller to create standalone .exe
"""

import os
import sys
import shutil
import subprocess

def clean_build():
    """Remove old build artifacts"""
    print("Cleaning old build files...")
    dirs_to_remove = ['build', 'dist']
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  Removed {dir_name}/")
    
def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        print(f"PyInstaller found: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("ERROR: PyInstaller not found!")
        print("Install with: pip install pyinstaller")
        return False

def build_executable():
    """Build the executable using PyInstaller"""
    print("\nBuilding ASRA_GCS.exe...")
    
    cmd = [
        'pyinstaller',
        '--name=ASRA_GCS',
        '--onefile',  # Single executable
        '--windowed',  # No console
        '--icon', 'resources/logo.png',
        '--add-data', 'resources;resources',
        '--add-data', 'README.md;.',
        '--hidden-import', 'pymavlink',
        '--hidden-import', 'pymavlink.dialects.v20.ardupilotmega',
        '--hidden-import', 'PIL',
        '--hidden-import', 'psutil',
        '--exclude-module', 'matplotlib',
        '--exclude-module', 'numpy',
        '--exclude-module', 'scipy',
        '--exclude-module', 'pandas',
        'asra_gcs_main.py'
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        print("\n✅ Build successful!")
        print(f"Executable: dist/ASRA_GCS.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed!")
        print(e.stderr)
        return False

def main():
    print("=" * 60)
    print("ASRA GCS - Windows Build Script")
    print("=" * 60)
    
    # Check prerequisites
    if not check_pyinstaller():
        sys.exit(1)
    
    # Clean old builds
    clean_build()
    
    # Build executable
    if build_executable():
        print("\n" + "=" * 60)
        print("Build complete! Next steps:")
        print("  1. Test: dist\\ASRA_GCS.exe")
        print("  2. Create installer with Inno Setup (optional)")
        print("=" * 60)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
