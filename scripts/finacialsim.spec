# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

block_cipher = None
project_root = Path.cwd()

a = Analysis(
    ["app/main.py"],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        ("app/reports/proposta.html", "app/reports"),
        ("app/reports/proposta.css", "app/reports"),
        ("docs", "docs"),
        ("alembic.ini", "."),
        ("app/data/migrations", "app/data/migrations"),
    ],
    hiddenimports=[
        "weasyprint", "scipy.optimize", "apscheduler", "bcrypt",
        "plotly.graph_objects", "nicegui",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

icon_path = "assets/icon.ico" if sys.platform.startswith("win") else "assets/icon.png"

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="FinacialSim",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=icon_path if Path(icon_path).exists() else None,
)
coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas,
    strip=False, upx=False, name="FinacialSim",
)
