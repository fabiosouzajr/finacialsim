# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

# SPECPATH is a PyInstaller built-in: dir containing this spec file (scripts/)
project_root = Path(SPECPATH).parent

a = Analysis(
    [str(project_root / "app/main.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        (str(project_root / "app/reports/proposta.html"), "app/reports"),
        (str(project_root / "app/reports/proposta.css"), "app/reports"),
        (str(project_root / "docs"), "docs"),
        (str(project_root / "alembic.ini"), "."),
        (str(project_root / "app/data/migrations"), "app/data/migrations"),
    ],
    hiddenimports=[
        "weasyprint", "apscheduler", "bcrypt",
        "plotly.graph_objects", "nicegui",
        "webview",
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

icon_path = str(project_root / ("assets/icon.ico" if sys.platform.startswith("win") else "assets/icon.png"))

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
