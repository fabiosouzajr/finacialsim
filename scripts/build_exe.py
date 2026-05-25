# Usage: pip install -e ".[build]" && python scripts/build_exe.py
"""Cross-platform PyInstaller builder."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    dist = project_root / "dist"
    build = project_root / "build"

    for path in (dist, build):
        if path.exists():
            shutil.rmtree(path)

    env = os.environ.copy()
    # On Windows, prepend GTK3-Runtime bin to PATH so the PyInstaller weasyprint hook
    # can discover libfontconfig, libpango, etc. via ctypes.util.find_library.
    if sys.platform.startswith("win"):
        gtk3_bin = Path("C:/Program Files/GTK3-Runtime Win64/bin")
        if gtk3_bin.exists():
            env["PATH"] = str(gtk3_bin) + os.pathsep + env.get("PATH", "")

    cmd = ["pyinstaller", "scripts/finacialsim.spec", "--clean", "--noconfirm"]
    print(">>", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=project_root, env=env)
    if proc.returncode != 0:
        return proc.returncode

    print("\nBuild complete. Output:")
    print(f"  - {dist / 'FinacialSim'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
