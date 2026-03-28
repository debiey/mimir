# Mimir Bash Integration
# Add to your ~/.bashrc: source ~/.mimir/source/scripts/mimir-bashrc.sh

MIMIR_DIR="/home/chioma/.mimir/source"
MIMIR_PYTHON="$MIMIR_DIR/venv/bin/python"

# Check if Mimir is installed
if [ -f "$MIMIR_PYTHON" ] && [ -d "$MIMIR_DIR/venv" ]; then
    
    # Function to get AI suggestion for unknown commands
    mimir_suggest() {
        local cmd="$1"
        cd "$MIMIR_DIR"
        source venv/bin/activate 2>/dev/null
        python3 -c "
import sys
sys.path.insert(0, '$MIMIR_DIR')
try:
    from core.copilot.ai_engine import AICopilot
    copilot = AICopilot(use_llm=True)
    result = copilot.suggest_command('$cmd')
    print(f'Suggested: {result[\"command\"]}')
    print(f'   {result[\"explanation\"]}')
except Exception as e:
    pass
" 2>/dev/null
        deactivate 2>/dev/null
    }
    
    # Custom command not found handler
    command_not_found_handle() {
        echo "Command not found: $1"
        mimir_suggest "$1"
        return 127
    }
    
    echo "Mimir integration active. Unknown commands will get AI suggestions."

else
    echo "Mimir not found. Please install Mimir first."
fi

