# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

# SPECPATH is a PyInstaller built-in: dir containing this spec file (scripts/)
project_root = Path(SPECPATH).parent

a = Analysis(
    ["app/main.py"],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        ("app/reports/proposta.html", "app/reports"),
        ("app/reports/proposta.css", "app/reports"),
        ("docs/*.md", "docs"),
        ("alembic.ini", "."),
        ("app/data/migrations", "app/data/migrations"),
    ],
    hiddenimports=[
        "weasyprint", "apscheduler", "bcrypt",
        "plotly.graph_objects", "nicegui",
        "pywebview",
        "sqlalchemy.dialects.sqlite",
        "jinja2",
        "loguru",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data)

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
    upx=False,  # disabled: UPX triggers AV false positives on Windows
    console=False,
    icon=icon_path if Path(icon_path).exists() else None,
)
coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas,
    strip=False, upx=False,  # disabled: UPX triggers AV false positives on Windows
    name="FinacialSim",
)
