# -*- mode: python ; coding: utf-8 -*-

datas = [
    ('preview_player.py', '.'),  # equivalent to --add-data="preview_player.py:."
    ('config.ini', '.'), 
    ('Sounds/*', 'Sounds')
]

binaries=[('/Applications/VLC.app/Contents/MacOS/lib/libvlc.5.dylib','.'), 
    ('/Applications/VLC.app/Contents/MacOS/lib/libvlccore.9.dylib', '.')]

hiddenimports = ['vlc', 'PyQt5.QtWidgets']

a = Analysis(
    ['DownloadYT.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name='DownloadYT',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['Youtube-dl.icns'],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DownloadYT',
)

app = BUNDLE(
    coll,
    name='DownloadYT.app',
    icon='Youtube-dl.icns',
    bundle_identifier=None,
)
