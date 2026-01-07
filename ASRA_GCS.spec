# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['asra_gcs_v2.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources', 'resources'),
        ('docs', 'docs'),
        ('README.md', '.'),
        ('CHANGELOG.md', '.'),
        ('V2_WHATS_NEW.md', '.')
    ],
    hiddenimports=[
        'pymavlink',
        'pymavlink.dialects.v20.ardupilotmega',
        'PIL',
        'psutil',
        'serial.tools.list_ports'
    ],
   hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'scipy', 'pandas', 'tkinter'],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ASRA_GCS_v2.0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources\\logo.png' if os.path.exists('resources\\logo.png') else None,
    version_info={
        'FileVersion': '2.0.0.0',
        'ProductVersion': '2.0.0.0',
        'FileDescription': 'ASRA Ground Control Station',
        'ProductName': 'ASRA GCS',
        'CompanyName': 'ASRA',
        'LegalCopyright': 'Copyright © 2026',
    }
)
