#!/bin/bash
# Mimir Enhanced Shell - AI-powered command line assistant

MIMIR_DIR="/home/chioma/.mimir/source"
MIMIR_PYTHON="$MIMIR_DIR/venv/bin/python"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Set prompt
PS1='\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\] [Mimir] '

# AI suggestion function
mimir_ai_suggest() {
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
    print(result['command'])
except Exception as e:
    pass
" 2>/dev/null
    deactivate 2>/dev/null
}

# Error analysis function
mimir_analyze_error() {
    local cmd="$1"
    local error="$2"
    cd "$MIMIR_DIR"
    source venv/bin/activate 2>/dev/null
    python3 -c "
import sys
sys.path.insert(0, '$MIMIR_DIR')
try:
    from core.copilot.ai_engine import AICopilot
    copilot = AICopilot(use_llm=True)
    prompt = f'The command \"{cmd}\" failed with error: {error[:500]}\nSuggest a fix.'
    result = copilot.llm.generate(prompt)
    print(result)
except Exception as e:
    pass
" 2>/dev/null
    deactivate 2>/dev/null
}

# Command not found handler
command_not_found_handle() {
    local cmd="$1"
    echo -e "${RED}Command not found: $cmd${NC}"
    echo -e "${YELLOW}Getting AI suggestion...${NC}"
    
    suggestion=$(mimir_ai_suggest "$cmd")
    if [ -n "$suggestion" ]; then
        echo -e "${GREEN}Suggested:${NC} $suggestion"
        read -p "Run this command? (y/N): " run_it
        if [[ "$run_it" == "y" || "$run_it" == "Y" ]]; then
            eval "$suggestion"
        fi
    fi
    return 127
}

# Welcome message
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║              MIMIR ENHANCED SHELL                       ║"
echo "║         AI-Powered Command Line Assistant               ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo "  Features: AI suggestions for unknown commands"
echo "  Type 'exit' to return"

# Start bash with enhanced features
exec bash --rcfile <(cat ~/.bashrc 2>/dev/null; echo "
command_not_found_handle() {
    local cmd=\"\$1\"
    echo -e \"${RED}Command not found: \$cmd${NC}\"
    suggestion=\$(mimir_ai_suggest \"\$cmd\" 2>/dev/null)
    if [ -n \"\$suggestion\" ]; then
        echo -e \"${GREEN}Suggested:${NC} \$suggestion\"
    fi
    return 127
}
export -f command_not_found_handle mimir_ai_suggest
")

