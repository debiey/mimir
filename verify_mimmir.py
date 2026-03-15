#!/usr/bin/env python3
"""Verify all Mimir components are working"""

def verify():
    print("🔍 Verifying Mimir Components...")
    print("="*50)
    
    # Check core modules
    try:
        from core.alerts.alert_manager import AlertManager
        print("✅ Alert Manager")
    except ImportError as e:
        print(f"❌ Alert Manager: {e}")
    
    try:
        from core.health.health_score import HealthScore
        print("✅ Health Score")
    except ImportError as e:
        print(f"❌ Health Score: {e}")
    
    try:
        from core.actuators.auto_healer import AutoHealer
        print("✅ Auto Healer")
    except ImportError as e:
        print(f"❌ Auto Healer: {e}")
    
    try:
        from interface.dashboard.live_dashboard import MimirDashboard
        print("✅ Dashboard")
    except ImportError as e:
        print(f"❌ Dashboard: {e}")
    
    try:
        from interface.cli.mimir_cli import MimirCLI
        print("✅ CLI Interface")
    except ImportError as e:
        print(f"❌ CLI Interface: {e}")
    
    print("="*50)

if __name__ == "__main__":
    verify()

