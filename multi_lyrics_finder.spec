# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['multi_lyrics_finder.py'],
    pathex=[],
    binaries=[],
    datas=[('locale', 'locale')],
    hiddenimports=[
        'plyer.platforms.win.notification',  # Windows notification backend
        'plyer.platforms.linux.notification',  # Linux notification backend
        'plyer.platforms.mac.notification',  # macOS notification backend
    ],
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
    name='multi_lyrics_finder',
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
)
