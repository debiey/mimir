#!/bin/bash
# Install Mimir Shell Integration

echo "🤖 Installing Mimir Shell Integration..."

# Check if Mimir is installed
if [ ! -d "/home/chioma/.mimir/source" ]; then
    echo "❌ Mimir not found. Please install Mimir first."
    exit 1
fi

# Add to .bashrc
BASHRC="$HOME/.bashrc"
INTEGRATION_LINE='source ~/.mimir/source/scripts/mimir-bashrc.sh'

if grep -q "$INTEGRATION_LINE" "$BASHRC"; then
    echo "✅ Already in .bashrc"
else
    echo "" >> "$BASHRC"
    echo "# Mimir Shell Integration" >> "$BASHRC"
    echo "$INTEGRATION_LINE" >> "$BASHRC"
    echo "✅ Added to .bashrc"
fi

# Add to .zshrc if it exists
if [ -f "$HOME/.zshrc" ]; then
    if grep -q "$INTEGRATION_LINE" "$HOME/.zshrc"; then
        echo "✅ Already in .zshrc"
    else
        echo "" >> "$HOME/.zshrc"
        echo "# Mimir Shell Integration" >> "$HOME/.zshrc"
        echo "$INTEGRATION_LINE" >> "$HOME/.zshrc"
        echo "✅ Added to .zshrc"
    fi
fi

echo ""
echo "🎉 Shell integration installed!"
echo ""
echo "To activate, either:"
echo "  1. Restart your terminal"
echo "  2. Run: source ~/.bashrc"
echo ""
echo "Now when you type an unknown command, Mimir will suggest what to use!"

