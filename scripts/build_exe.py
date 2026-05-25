"""Cross-platform PyInstaller builder."""

from __future__ import annotations

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

    cmd = ["pyinstaller", "scripts/finacialsim.spec", "--clean", "--noconfirm"]
    print(">>", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=project_root)
    if proc.returncode != 0:
        return proc.returncode

    print("\nBuild complete. Output:")
    print(f"  - {dist / 'FinacialSim'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
