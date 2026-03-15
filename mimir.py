#!/usr/bin/env python3
"""Mimir main entry point"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def main():
    print("\n" + "="*60)
    print("          🤖 MIMIR v2.0")
    print("     Intelligent Linux Companion")
    print("="*60)
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "cli":
            from interface.cli.mimir_cli import main as cli_main
            cli_main()
        elif cmd == "status":
            from core.sensors.system_monitor import quick_status
            quick_status()
        elif cmd in ["-h", "--help"]:
            show_help()
        else:
            print(f"Unknown command: {cmd}")
            show_help()
    else:
        try:
            from interface.cli.mimir_cli import main as cli_main
            cli_main()
        except ImportError:
            basic_mode()

def show_help():
    print("""
Usage: mimir [command]

Commands:
  cli       Start interactive CLI
  status    Show quick system status
  help      Show this help

Examples:
  mimir
  mimir status
  mimir cli
""")

def basic_mode():
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        print(f"\n📊 Basic System Status:")
        print(f"  CPU:     {cpu:6.1f}%")
        print(f"  Memory:  {mem.percent:6.1f}%")
    except ImportError:
        print("Please install psutil: pip install psutil")

if __name__ == "__main__":
    main()

