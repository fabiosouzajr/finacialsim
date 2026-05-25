#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
DIST="$ROOT/dist"
APP_NAME="FinacialSim.app"

# 1. PyInstaller produces a folder; we wrap it into .app
python "$ROOT/scripts/build_exe.py"

# 2. Create .app structure
APP="$DIST/$APP_NAME"
rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS"
mkdir -p "$APP/Contents/Resources"
cp -r "$DIST/FinacialSim/." "$APP/Contents/MacOS/"
cp "$ROOT/assets/icon.png" "$APP/Contents/Resources/icon.png"

# 3. Info.plist
cat > "$APP/Contents/Info.plist" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
"http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleName</key><string>FinacialSim</string>
  <key>CFBundleDisplayName</key><string>FinacialSim</string>
  <key>CFBundleIdentifier</key><string>com.finacialsim.app</string>
  <key>CFBundleVersion</key><string>1.0.0</string>
  <key>CFBundleExecutable</key><string>FinacialSim</string>
  <key>CFBundleIconFile</key><string>icon</string>
  <key>LSMinimumSystemVersion</key><string>12.0</string>
</dict>
</plist>
EOF

# 4. Ad-hoc sign (allows running locally without notarization)
codesign --deep --force --sign - "$APP"

# 5. DMG (requires create-dmg: brew install create-dmg)
create-dmg \
  --volname "FinacialSim Installer" \
  --window-size 600 400 \
  --app-drop-link 425 185 \
  --icon "$APP_NAME" 175 185 \
  "$DIST/FinacialSim-1.0.0.dmg" \
  "$APP"

echo "DMG at $DIST/FinacialSim-1.0.0.dmg"
