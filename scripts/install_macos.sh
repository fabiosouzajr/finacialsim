#!/usr/bin/env bash
set -euo pipefail

DMG_URL="${1:-https://github.com/your-org/finacialsim/releases/latest/download/FinacialSim-1.0.0.dmg}"

if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew nao detectado. Instalando..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# WeasyPrint native deps
brew install pango gdk-pixbuf libffi

TMP=$(mktemp -d)
trap 'hdiutil detach /Volumes/FinacialSim 2>/dev/null; rm -rf "$TMP"' EXIT
curl -fL "$DMG_URL" -o "$TMP/finacialsim.dmg"
hdiutil attach "$TMP/finacialsim.dmg" -mountpoint /Volumes/FinacialSim
sudo cp -R "/Volumes/FinacialSim/FinacialSim.app" /Applications/
hdiutil detach /Volumes/FinacialSim
rm -rf "$TMP"

echo "FinacialSim instalado em /Applications/FinacialSim.app"
