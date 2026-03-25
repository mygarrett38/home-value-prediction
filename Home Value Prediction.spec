# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src\\runner.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\nhiel\\AppData\\Local\\Python\\pythoncore-3.14-64\\Lib\\site-packages\\xgboost', 'xgboost'), ('.env', '.'), ('model', 'model'), ('src/widgets/home-value-window.ui', 'src/widgets')],
    hiddenimports=['xgboost.core'],
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
    name='Home Value Prediction',
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
    icon=['src\\widgets\\icons\\home.ico'],
)
