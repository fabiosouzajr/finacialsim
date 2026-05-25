#!/usr/bin/env bash
set -euo pipefail

APPIMAGE_URL="${1:-https://github.com/your-org/finacialsim/releases/latest/download/FinacialSim-x86_64.AppImage}"
INSTALL_DIR="/opt/finacialsim"
DESKTOP_FILE="$HOME/.local/share/applications/finacialsim.desktop"

sudo mkdir -p "$INSTALL_DIR"
sudo curl -fL "$APPIMAGE_URL" -o "$INSTALL_DIR/FinacialSim.AppImage"
sudo chmod +x "$INSTALL_DIR/FinacialSim.AppImage"

mkdir -p "$(dirname "$DESKTOP_FILE")"
cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Name=FinacialSim
Comment=Simulador de financiamento de veiculos
Exec=$INSTALL_DIR/FinacialSim.AppImage
Icon=utilities-terminal
Terminal=false
Type=Application
Categories=Office;Finance;
EOF

echo "FinacialSim instalado em $INSTALL_DIR"
echo "Inicie pelo menu de aplicativos ou via: $INSTALL_DIR/FinacialSim.AppImage"
