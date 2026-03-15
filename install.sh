#!/bin/bash
# Mimir Master Installer

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_step() { echo -e "\n${BLUE}➤${NC} ${CYAN}$1${NC}"; }
print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; exit 1; }

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed."
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_success "Python $PYTHON_VERSION detected"

# Create Mimir home
MIMIR_HOME="$HOME/.mimir"
mkdir -p "$MIMIR_HOME"
cd "$MIMIR_HOME"

print_success "Created $MIMIR_HOME"

# Copy source to Mimir home
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$MIMIR_HOME/source"
cp -r "$SCRIPT_DIR"/* "$MIMIR_HOME/source/"
cp -r "$SCRIPT_DIR"/.* "$MIMIR_HOME/source/" 2>/dev/null || true
cd "$MIMIR_HOME/source"

print_success "Source code copied"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
print_success "Virtual environment created"

# Install dependencies
pip install -r requirements.txt > /dev/null 2>&1
print_success "Python packages installed"

# Create launcher
mkdir -p "$HOME/.local/bin"
cat > "$HOME/.local/bin/mimir" << LAUNCHEREOF
#!/bin/bash
cd "$MIMIR_HOME/source"
source venv/bin/activate
python mimir.py "\$@"
LAUNCHEREOF

chmod +x "$HOME/.local/bin/mimir"
print_success "Launcher created at ~/.local/bin/mimir"

# Create uninstaller
cat > tools/uninstall.sh << UNINSTALLEOF
#!/bin/bash
read -p "Remove Mimir completely? (y/N) " -n 1 -r
echo
if [[ \$REPLY =~ ^[Yy]\$ ]]; then
    rm -rf "$MIMIR_HOME"
    rm -f "$HOME/.local/bin/mimir"
    echo "✅ Mimir uninstalled"
else
    echo "❌ Uninstall cancelled"
fi
UNINSTALLEOF

chmod +x tools/uninstall.sh
print_success "Uninstall script created"

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ MIMIR INSTALLATION COMPLETE!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "🚀 To start Mimir:"
echo "   mimir"
echo ""
echo "📁 Installation: $MIMIR_HOME"
echo ""
echo "🗑️  To uninstall:"
echo "   $MIMIR_HOME/source/tools/uninstall.sh"
echo ""

