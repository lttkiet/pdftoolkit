# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller build spec for PDFToolkit."""

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        "src.app",
        "src.viewer",
        "src.utils.file_ops",
        "src.tools.merge",
        "src.tools.split",
        "src.tools.rotate",
        "src.tools.reorder",
        "src.tools.add_content",
        "src.tools.extract_text",
        "src.tools.compress",
        "src.tools.watermark",
        "src.tools.encrypt",
        "src.tools.convert",
        "src.tools.metadata",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="PDFToolkit",
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
