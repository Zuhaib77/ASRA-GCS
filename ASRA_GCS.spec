# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['asra_gcs_main.py'],
    pathex=[],
    binaries=[],
    datas=[('resources', 'resources'), ('README.md', '.')],
    hiddenimports=['pymavlink', 'pymavlink.dialects.v20.ardupilotmega', 'PIL', 'psutil'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'scipy', 'pandas'],
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
    name='ASRA_GCS',
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
    icon=['resources\\logo.png'],
)
