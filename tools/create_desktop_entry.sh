#!/bin/bash
cat > ~/.local/share/applications/mimir.desktop << EOF
[Desktop Entry]
Name=Mimir
Comment=Intelligent Linux Companion
Exec=$HOME/.local/bin/mimir
Icon=$HOME/.mimir/assets/icon.png
Terminal=true
Type=Application
Categories=System;Utility;
EOF
echo "✅ Desktop entry created"

