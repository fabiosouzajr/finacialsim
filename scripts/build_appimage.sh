#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
DIST="$ROOT/dist"
APPDIR="$DIST/FinacialSim.AppDir"
APPIMAGE_TOOL="${APPIMAGE_TOOL:-appimagetool-x86_64.AppImage}"

# 1. Run PyInstaller first
python "$ROOT/scripts/build_exe.py"

# 2. Build AppDir
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"
cp -r "$DIST/FinacialSim/." "$APPDIR/usr/bin/"

# 3. Desktop + icon
cp "$ROOT/scripts/finacialsim.desktop" "$APPDIR/finacialsim.desktop"
cp "$ROOT/assets/icon.png" "$APPDIR/finacialsim.png"
cp "$ROOT/assets/icon.png" "$APPDIR/.DirIcon"

# 4. AppRun
cat > "$APPDIR/AppRun" <<'EOF'
#!/bin/sh
HERE=$(dirname "$(readlink -f "$0")")
exec "$HERE/usr/bin/FinacialSim" "$@"
EOF
chmod +x "$APPDIR/AppRun"

# 5. Build AppImage (requires appimagetool in PATH or APPIMAGE_TOOL env var)
"$APPIMAGE_TOOL" "$APPDIR" "$DIST/FinacialSim-x86_64.AppImage"
echo "AppImage created at $DIST/FinacialSim-x86_64.AppImage"
