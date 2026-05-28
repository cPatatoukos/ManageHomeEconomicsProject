# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

block_cipher = None

matplotlib_datas, matplotlib_binaries, matplotlib_hiddenimports = collect_all("matplotlib")
openpyxl_datas, openpyxl_binaries, openpyxl_hiddenimports = collect_all("openpyxl")

datas = [("schema.sql", ".")]
datas += matplotlib_datas
datas += openpyxl_datas

binaries = matplotlib_binaries + openpyxl_binaries

hiddenimports = matplotlib_hiddenimports + openpyxl_hiddenimports + [
    "tkinter",
    "tkinter.ttk",
    "tkinter.messagebox",
    "tkinter.filedialog",
]

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="FamilyFinance",
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
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="FamilyFinance",
)

app = BUNDLE(
    coll,
    name="FamilyFinance.app",
    icon=None,
    bundle_identifier="com.familyfinance.app",
)
