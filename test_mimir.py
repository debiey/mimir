#!/usr/bin/env python3
"""Quick test for Mimir dependencies"""

def test_imports():
    print("Testing Mimir dependencies...")
    
    try:
        import psutil
        print(f"✅ psutil {psutil.__version__}")
    except ImportError:
        print("❌ psutil not installed")
        return False
    
    try:
        import rich
        print(f"✅ rich {rich.__version__}")
    except ImportError:
        print("❌ rich not installed")
        return False
    
    print("\n✅ All core dependencies installed!")
    return True

if __name__ == "__main__":
    test_imports()

