#!/usr/bin/env python3
"""Mimir - Advanced Linux Companion"""
import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    print("\n" + "="*60)
    print("          🤖 MIMIR v4.0")
    print("     Advanced Linux Companion with AI")
    print("="*60)
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "cli":
            from interface.cli.advanced_cli import main as cli_main
            cli_main()
        elif cmd == "status":
            from core.sensors.system_monitor import quick_status
            quick_status()
        elif cmd == "web":
            print("\n🌐 Starting Mimir Web Interface...")
            from interface.web.copilot_web import app
            app.run(host='0.0.0.0', port=5000, debug=False)
        elif cmd in ["-h", "--help"]:
            show_help()
        else:
            print(f"Unknown command: {cmd}")
            show_help()
    else:
        # Default: start CLI
        from interface.cli.advanced_cli import main as cli_main
        cli_main()

def show_help():
    print("""
Usage: mimir [command]

Commands:
  cli       Start interactive CLI (default)
  status    Show quick system status
  web       Launch web interface
  help      Show this help

Examples:
  mimir
  mimir status
  mimir web
  mimir cli
""")

if __name__ == "__main__":
    main()

