#!/bin/bash
read -p "Remove Mimir completely? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "$HOME/.mimir"
    rm -f "$HOME/.local/bin/mimir"
    echo "✅ Mimir uninstalled"
else
    echo "❌ Uninstall cancelled"
fi

