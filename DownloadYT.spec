# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['DownloadYT.py'],
    pathex=[],
    binaries=[],
    datas=[('config.ini', '.'),('Sounds/*', 'Sounds')],
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
