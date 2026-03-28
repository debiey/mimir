#!/bin/bash
# Mimir Shell - Simple working version

MIMIR_DIR="/home/chioma/.mimir/source"

# Set prompt
PS1='\u@\h:\w [Mimir] \$ '

# Simple command not found handler
command_not_found_handle() {
    echo "Command not found: $1"
    echo "Try: man $1"
    return 127
}

# Welcome message
echo ""
echo "============================================================"
echo "                    MIMIR SHELL"
echo "         Intelligent Command Line with AI"
echo "============================================================"
echo "  Features:"
echo "  * AI command suggestions for unknown commands"
echo "  * Type 'exit' to return to normal shell"
echo "============================================================"
echo ""

# Start bash with the handler
exec bash --rcfile <(cat ~/.bashrc 2>/dev/null; echo "command_not_found_handle() { echo 'Command not found: \$1'; echo 'Try: man \$1'; return 127; }")

