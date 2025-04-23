# -*- mode: python ; coding: utf-8 -*-
import sys
import os

# Include the source path so PyInstaller can find your modules
sys.path.append(os.path.abspath('src/main/python'))

# Include the .env file in the root of the bundle
datas = [('.env', '.')]

a = Analysis(
    ['src/main/python/advisor/RunAdvisorBot.py'],  # Use forward slashes for cross-platform compatibility
    pathex=[os.path.abspath('.')],                 # Make sure current dir is in path
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='RunAdvisorBot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want the console window visible for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='src/main/python/advisor/money_robot_Q94_icon.ico',  # Correct path without list
)
