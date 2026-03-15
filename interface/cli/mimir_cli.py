"""Mimir CLI interface - Complete version with all features"""
import cmd
import sys
import psutil
import time
import os
from datetime import datetime
from pathlib import Path

# Import Mimir modules (with error handling)
try:
    from core.health.health_score import HealthScore
    HEALTH_AVAILABLE = True
except ImportError:
    HEALTH_AVAILABLE = False

try:
    from core.alerts.alert_manager import AlertManager
    ALERTS_AVAILABLE = True
except ImportError:
    ALERTS_AVAILABLE = False

try:
    from core.actuators.auto_healer import AutoHealer
    HEALER_AVAILABLE = True
except ImportError:
    HEALER_AVAILABLE = False

try:
    from core.copilot.ai_engine import AICopilot
    COPILOT_AVAILABLE = True
except ImportError:
    COPILOT_AVAILABLE = False

class MimirCLI(cmd.Cmd):
    """Mimir Command Line Interface - Intelligent Linux Companion"""
    
    intro = """
╔══════════════════════════════════════════════════════════╗
║                     M I M I R                            ║
║              Intelligent Linux Companion                 ║
║                      v2.0.0                              ║
╠══════════════════════════════════════════════════════════╣
║  Type 'help' for commands  |  'dashboard' for live view  ║
║  Type 'copilot' for AI help  |  'web' for browser UI     ║
╚══════════════════════════════════════════════════════════╝
"""
    prompt = "mimir> "
    
    def __init__(self):
        super().__init__()
        self.start_time = time.time()
        self.command_count = 0
        self.health = HealthScore() if HEALTH_AVAILABLE else None
        self.alert_mgr = AlertManager() if ALERTS_AVAILABLE else None
        self.healer = AutoHealer() if HEALER_AVAILABLE else None
        self.copilot = AICopilot() if COPILOT_AVAILABLE else None
        self.in_copilot_mode = False
        
    # ==================== HELPER METHODS ====================
    
    def _get_color(self, value, warn, crit):
        """Get color code based on value"""
        if value >= crit:
            return '\033[91m'  # Red
        elif value >= warn:
            return '\033[93m'  # Yellow
        else:
            return '\033[92m'  # Green
    
    def _reset(self):
        """Reset color"""
        return '\033[0m'
    
    # ==================== COMMAND DISPATCH ====================
    
    def default(self, line):
        """Handle unknown commands"""
        if self.in_copilot_mode:
            # In copilot mode, try to handle as copilot command
            if line.startswith('suggest '):
                self.do_suggest(line[8:])
            elif line.startswith('explain '):
                self.do_explain(line[8:])
            elif line.startswith('diagnose '):
                self.do_diagnose(line[8:])
            elif line == 'diagnose':
                self.do_diagnose('')
            elif line == 'optimize':
                self.do_optimize('')
            elif line == 'back':
                self.do_back('')
            elif line == 'help':
                self.do_copilot_help('')
            else:
                print(f"Unknown copilot command: {line}")
                print("Type 'help' for available copilot commands")
        else:
            print(f"Unknown command: {line}")
            print("Type 'help' for available commands")
    
    # ==================== WEB INTERFACE COMMAND ====================
    
    def do_web(self, arg):
        """Launch web-based copilot interface in browser"""
        self.command_count += 1
        print("\n🌐 Starting Mimir Web Interface...")
        print("Opening browser to http://localhost:5000")
        print("Press Ctrl+C to stop the web server\n")
        
        import subprocess
        import threading
        import webbrowser
        
        def run_server():
            import sys
            import os
            sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
            try:
                from interface.web.copilot_web import app
                app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
            except ImportError as e:
                print(f"\n❌ Failed to start web server: {e}")
                print("   Make sure flask is installed: pip install flask flask-cors")
            except Exception as e:
                print(f"\n❌ Web server error: {e}")
        
        # Start server in background
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Wait a moment for server to start
        time.sleep(2)
        
        # Open browser
        webbrowser.open('http://localhost:5000')
        
        # Get local IP for network access
        try:
            import socket
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            print(f"\n✅ Web interface running at:")
            print(f"   • Local: http://localhost:5000")
            print(f"   • Network: http://{local_ip}:5000")
        except:
            print(f"\n✅ Web interface running at: http://localhost:5000")
        
        print("\n⚠️  Press Ctrl+C to return to Mimir CLI (web server continues in background)")
        print("   To stop the web server completely, run: pkill -f copilot_web.py")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Returning to Mimir CLI. Web server continues running.")
            print("   To stop the web server: pkill -f copilot_web.py")
    
    # ==================== COPILOT MODE COMMANDS ====================
    
    def do_copilot(self, arg):
        """Enter copilot mode for AI assistance"""
        self.command_count += 1
        self.in_copilot_mode = True
        self.prompt = "copilot> "
        print("\n" + "="*60)
        print("🤖 MIMIR COPILOT MODE")
        print("="*60)
        print("I'm here to help you with Linux commands and system issues.")
        print("\nAvailable commands:")
        print("  suggest [task]  - Suggest command for a task")
        print("  explain [cmd]   - Explain what a command does")
        print("  diagnose [issue] - Diagnose system issues")
        print("  optimize        - Suggest optimizations")
        print("  back            - Return to main Mimir CLI")
        print("  help            - Show this help")
    
    def do_suggest(self, arg):
        """Suggest a Linux command: suggest [task description]"""
        self.command_count += 1
        if not arg:
            print("Usage: suggest [task description]")
            print("Example: suggest find large files")
            return
        
        if not COPILOT_AVAILABLE or not self.copilot:
            print("Copilot module not available. Install core.copilot.ai_engine")
            return
        
        print(f"\n🔍 Analyzing task: '{arg}'")
        suggestion = self.copilot.suggest_command(arg)
        
        print(f"\n💡 Suggested command:")
        print(f"   {suggestion['command']}")
        print(f"\n📝 Explanation: {suggestion['explanation']}")
        print(f"   Confidence: {suggestion['confidence']*100:.0f}%")
        
        # Ask if user wants to run it
        run = input("\nRun this command? (y/N): ").lower()
        if run == 'y':
            import subprocess
            print(f"\n🚀 Running: {suggestion['command']}")
            try:
                result = subprocess.run(suggestion['command'], 
                                      shell=True, text=True, 
                                      capture_output=True)
                print(result.stdout)
                if result.stderr:
                    print(f"⚠️  Errors: {result.stderr}")
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def do_explain(self, arg):
        """Explain a Linux command: explain [command]"""
        self.command_count += 1
        if not arg:
            print("Usage: explain [command]")
            print("Example: explain ls -la")
            return
        
        if not COPILOT_AVAILABLE or not self.copilot:
            print("Copilot module not available. Install core.copilot.ai_engine")
            return
        
        print(f"\n🔍 Analyzing command: '{arg}'")
        explanation = self.copilot.explain_command(arg)
        
        print(f"\n📖 Command: {explanation['command']}")
        print(f"📝 {explanation['explanation']}")
        
        if explanation.get('examples'):
            print(f"\n💡 Examples:")
            for ex in explanation['examples']:
                print(f"   • {ex}")
    
    def do_diagnose(self, arg):
        """Diagnose system issues: diagnose [slow|memory|disk|cpu|network|crash]"""
        self.command_count += 1
        
        if not COPILOT_AVAILABLE or not self.copilot:
            print("Copilot module not available. Install core.copilot.ai_engine")
            return
        
        issue = arg if arg else "general"
        print(f"\n🔍 Diagnosing: {issue} issues...")
        
        diagnosis = self.copilot.diagnose_issue(issue)
        
        print(f"\n📋 DIAGNOSIS: {diagnosis['issue']}")
        print("="*50)
        
        print("\n🔴 Findings:")
        for finding in diagnosis['diagnosis']:
            print(f"  • {finding}")
        
        print("\n💡 Suggestions:")
        for suggestion in diagnosis['suggestions']:
            print(f"  • {suggestion}")
        
        if 'severity' in diagnosis:
            if diagnosis['severity'] == 'critical':
                print("\n🚨 CRITICAL - Take action immediately!")
            elif diagnosis['severity'] == 'warning':
                print("\n⚠️  Warning - Monitor this issue")
    
    def do_optimize(self, arg):
        """Suggest system optimizations"""
        self.command_count += 1
        
        if not COPILOT_AVAILABLE or not self.copilot:
            print("Copilot module not available. Install core.copilot.ai_engine")
            return
        
        print("\n🔧 ANALYZING FOR OPTIMIZATIONS...")
        print("="*50)
        
        optimizations = self.copilot.suggest_optimization()
        
        if optimizations:
            for opt in optimizations:
                print(f"\n📌 {opt['area'].upper()}: {opt['suggestion']}")
                if 'command' in opt:
                    print(f"   Command: {opt['command']}")
                if 'processes' in opt:
                    print(f"   Processes: {opt['processes']}")
                print(f"   Benefit: {opt['benefit']}")
        else:
            print("\n✅ System is already well optimized!")
    
    def do_back(self, arg):
        """Return to main Mimir CLI from copilot mode"""
        self.in_copilot_mode = False
        self.prompt = "mimir> "
        print("\nReturning to main Mimir CLI...")
    
    def do_copilot_help(self, arg):
        """Show copilot help"""
        print("""
🤖 COPILOT MODE COMMANDS:

suggest [task]     - Suggest command for a task
                     Example: suggest find large files

explain [cmd]      - Explain what a command does
                     Example: explain grep -r

diagnose [issue]   - Diagnose system issues
                     Issues: slow, memory, disk, cpu, network, crash
                     Example: diagnose slow

optimize           - Suggest system optimizations

back               - Return to main Mimir CLI

help               - Show this help
""")
    
    # ==================== BASIC SYSTEM COMMANDS ====================
    
    def do_status(self, arg):
        """Show comprehensive system status"""
        self.command_count += 1
        
        # Gather metrics
        cpu = psutil.cpu_percent(interval=1)
        cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        disk = psutil.disk_usage('/')
        net = psutil.net_io_counters()
        processes = len(psutil.pids())
        uptime_seconds = time.time() - psutil.boot_time()
        uptime_days = uptime_seconds / 86400
        load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else (0, 0, 0)
        
        # System info
        hostname = os.uname().nodename
        kernel = os.uname().release
        
        # Create beautiful output
        print(f"\n{'='*60}")
        print(f"📊 SYSTEM STATUS REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        print(f"Host: {hostname} | Kernel: {kernel}")
        print(f"{'='*60}")
        
        # CPU Section
        cpu_color = self._get_color(cpu, 70, 90)
        print(f"\n🔥 CPU:")
        print(f"  Total: {cpu_color}{cpu:5.1f}%{self._reset()}")
        print(f"  Per Core: ", end="")
        for i, core in enumerate(cpu_per_core[:8]):  # Show first 8 cores
            core_color = self._get_color(core, 70, 90)
            print(f"{core_color}{core:3.0f}%{self._reset()} ", end="")
        print()
        print(f"  Load Avg: {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}")
        
        # Memory Section
        mem_color = self._get_color(memory.percent, 80, 95)
        print(f"\n💾 Memory:")
        print(f"  RAM:    {mem_color}{memory.percent:5.1f}%{self._reset()}  Used: {memory.used/1024**3:.2f}/{memory.total/1024**3:.2f} GB")
        print(f"  Swap:   {swap.percent:5.1f}%  Used: {swap.used/1024**3:.2f}/{swap.total/1024**3:.2f} GB")
        print(f"  Available: {memory.available/1024**3:.2f} GB")
        
        # Disk Section
        disk_color = self._get_color(disk.percent, 80, 95)
        print(f"\n💽 Disk:")
        print(f"  /:      {disk_color}{disk.percent:5.1f}%{self._reset()}  Used: {disk.used/1024**3:.2f}/{disk.total/1024**3:.2f} GB")
        print(f"  Free:   {disk.free/1024**3:.2f} GB")
        
        # Network Section
        print(f"\n🌐 Network:")
        print(f"  Sent:     {net.bytes_sent/1024**2:8.2f} MB")
        print(f"  Received: {net.bytes_recv/1024**2:8.2f} MB")
        
        # System Section
        print(f"\n⚙️ System:")
        print(f"  Processes: {processes}")
        print(f"  Uptime:    {int(uptime_days)}d {int((uptime_seconds%86400)/3600)}h {int((uptime_seconds%3600)/60)}m")
        
        # Health score if available
        if HEALTH_AVAILABLE and self.health:
            score = self.health.get_score()
            emoji = self.health.get_emoji()
            print(f"\n{emoji} Health Score: {score:.1f}/100")
        
        # Alerts if any
        if ALERTS_AVAILABLE and self.alert_mgr:
            alerts = self.alert_mgr.check_all()
            if alerts:
                print(f"\n🚨 Active Alerts: {len(alerts)}")
                for alert in alerts[:3]:
                    print(f"  {alert}")
        
        print(f"\n{'='*60}")
    
    def do_top(self, arg):
        """Show top processes by CPU and memory"""
        self.command_count += 1
        
        n = 10
        if arg and arg.isdigit():
            n = int(arg)
        
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                processes.append(proc.info)
            except:
                pass
        
        # CPU Table
        print(f"\n🔥 TOP {n} PROCESSES BY CPU")
        print("-" * 60)
        processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        print(f"{'PID':>6} {'CPU%':>6} {'MEM%':>6} {'STATUS':>8}  NAME")
        print("-" * 60)
        for proc in processes[:n]:
            if proc['cpu_percent'] > 0:
                cpu_color = self._get_color(proc['cpu_percent'], 50, 80)
                print(f"{proc['pid']:6d} {cpu_color}{proc['cpu_percent']:6.1f}{self._reset()} {proc['memory_percent']:6.1f} {proc['status']:>8}  {proc['name'][:30]}")
        
        # Memory Table
        print(f"\n💾 TOP {n} PROCESSES BY MEMORY")
        print("-" * 60)
        processes.sort(key=lambda x: x.get('memory_percent', 0), reverse=True)
        print(f"{'PID':>6} {'MEM%':>6} {'CPU%':>6} {'STATUS':>8}  NAME")
        print("-" * 60)
        for proc in processes[:n]:
            if proc['memory_percent'] > 0:
                mem_color = self._get_color(proc['memory_percent'], 10, 20)
                print(f"{proc['pid']:6d} {mem_color}{proc['memory_percent']:6.1f}{self._reset()} {proc['cpu_percent']:6.1f} {proc['status']:>8}  {proc['name'][:30]}")
    
    def do_memory(self, arg):
        """Show detailed memory information"""
        self.command_count += 1
        
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        print(f"\n💾 DETAILED MEMORY REPORT")
        print(f"{'='*50}")
        
        # RAM details
        print(f"\nRAM:")
        print(f"  Total:     {memory.total / 1024**3:10.2f} GB")
        print(f"  Available: {memory.available / 1024**3:10.2f} GB")
        print(f"  Used:      {memory.used / 1024**3:10.2f} GB ({memory.percent}%)")
        print(f"  Free:      {memory.free / 1024**3:10.2f} GB")
        
        # Memory breakdown
        print(f"\n  Breakdown:")
        print(f"    Active:   {memory.active / 1024**3:10.2f} GB")
        print(f"    Inactive: {memory.inactive / 1024**3:10.2f} GB")
        print(f"    Buffers:  {memory.buffers / 1024**3:10.2f} GB")
        print(f"    Cached:   {memory.cached / 1024**3:10.2f} GB")
        print(f"    Shared:   {memory.shared / 1024**3:10.2f} GB")
        
        # Swap details
        print(f"\nSwap:")
        print(f"  Total: {swap.total / 1024**3:10.2f} GB")
        print(f"  Used:  {swap.used / 1024**3:10.2f} GB ({swap.percent}%)")
        print(f"  Free:  {swap.free / 1024**3:10.2f} GB")
    
    def do_disk(self, arg):
        """Show detailed disk usage"""
        self.command_count += 1
        
        print(f"\n💽 DISK USAGE REPORT")
        print(f"{'='*50}")
        
        # All partitions
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                color = self._get_color(usage.percent, 80, 95)
                
                print(f"\n{part.mountpoint} ({part.fstype}):")
                print(f"  Device: {part.device}")
                print(f"  Size:   {usage.total / 1024**3:8.2f} GB")
                print(f"  Used:   {color}{usage.used / 1024**3:8.2f} GB ({usage.percent}%){self._reset()}")
                print(f"  Free:   {usage.free / 1024**3:8.2f} GB")
            except:
                pass
        
        # Disk I/O
        disk_io = psutil.disk_io_counters()
        if disk_io:
            print(f"\n📊 Disk I/O:")
            print(f"  Read:  {disk_io.read_bytes / 1024**2:8.2f} MB")
            print(f"  Write: {disk_io.write_bytes / 1024**2:8.2f} MB")
    
    def do_network(self, arg):
        """Show network information"""
        self.command_count += 1
        
        net = psutil.net_io_counters()
        connections = psutil.net_connections()
        
        print(f"\n🌐 NETWORK REPORT")
        print(f"{'='*50}")
        
        # Traffic stats
        print(f"\n📊 Traffic:")
        print(f"  Sent:     {net.bytes_sent / 1024**2:10.2f} MB")
        print(f"  Received: {net.bytes_recv / 1024**2:10.2f} MB")
        print(f"  Packets sent: {net.packets_sent}")
        print(f"  Packets recv: {net.packets_recv}")
        
        # Connection stats
        print(f"\n🔌 Connections:")
        status_count = {}
        for conn in connections[:500]:
            status_count[conn.status] = status_count.get(conn.status, 0) + 1
        
        for status, count in status_count.items():
            print(f"  {status}: {count}")
    
    def do_health(self, arg):
        """Show system health score and breakdown"""
        self.command_count += 1
        
        if not HEALTH_AVAILABLE or not self.health:
            print("Health module not available. Install core.health.health_score")
            return
        
        score = self.health.get_score()
        details = self.health.get_details()
        
        print(f"\n{self.health.get_emoji()} SYSTEM HEALTH SCORE: {score:.1f}/100\n")
        
        # Create a visual bar
        bar_length = 40
        filled = int(score / 100 * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        if score >= 80:
            color = '\033[92m'  # Green
        elif score >= 60:
            color = '\033[93m'  # Yellow
        else:
            color = '\033[91m'  # Red
        
        print(f"  {color}[{bar}]{self._reset()} {score:.1f}%\n")
        print("Breakdown:")
        print("-" * 50)
        
        for component, data in details['breakdown'].items():
            # Status emoji
            if data['status'] == 'good':
                emoji = "🟢"
            elif data['status'] == 'warning':
                emoji = "🟡"
            else:
                emoji = "🔴"
            
            # Component bar
            comp_bar_length = 20
            comp_filled = int(data['score'] / data['max'] * comp_bar_length)
            comp_bar = "█" * comp_filled + "░" * (comp_bar_length - comp_filled)
            
            print(f"{emoji} {component.upper():8}: [{comp_bar}] {data['score']:.1f}/{data['max']} ({data['value']:.1f})")
    
    def do_alerts(self, arg):
        """Show active alerts and history"""
        self.command_count += 1
        
        if not ALERTS_AVAILABLE or not self.alert_mgr:
            print("Alert module not available. Install core.alerts.alert_manager")
            return
        
        if arg == 'history':
            # Show alert history
            history = self.alert_mgr.get_alert_history(20)
            if history:
                print(f"\n📜 Recent Alert History:")
                print("-" * 60)
                for alert in history:
                    emoji = "🔴" if alert['severity'] == 'critical' else "🟡"
                    print(f"{emoji} [{alert['timestamp'][:19]}] {alert['message']}")
            else:
                print("\n✅ No alert history")
        else:
            # Show active alerts
            alerts = self.alert_mgr.check_all()
            
            if alerts:
                print(f"\n🚨 ACTIVE ALERTS ({len(alerts)}):")
                print("-" * 60)
                for alert in alerts:
                    emoji = "🔴" if alert.severity == 'critical' else "🟡"
                    print(f"{emoji} [{alert.severity.upper()}] {alert.message}")
            else:
                print("\n✅ No active alerts")
    
    def do_monitor(self, arg):
        """Start continuous monitoring (Ctrl+C to stop)"""
        self.command_count += 1
        
        if not ALERTS_AVAILABLE or not self.alert_mgr:
            print("Alert module not available. Install core.alerts.alert_manager")
            return
        
        interval = 30  # seconds
        if arg and arg.isdigit():
            interval = int(arg)
        
        print(f"\n🚀 Starting continuous monitoring (checking every {interval}s)")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                # Clear line
                print("\033[K", end="")
                
                # Check metrics
                cpu = psutil.cpu_percent()
                mem = psutil.virtual_memory().percent
                disk = psutil.disk_usage('/').percent
                
                # Check for alerts
                alerts = self.alert_mgr.check_all()
                self.alert_mgr.send_notifications()
                
                # Display status
                timestamp = datetime.now().strftime('%H:%M:%S')
                
                cpu_color = self._get_color(cpu, 70, 90)
                mem_color = self._get_color(mem, 80, 95)
                disk_color = self._get_color(disk, 80, 95)
                
                print(f"[{timestamp}] "
                      f"CPU: {cpu_color}{cpu:5.1f}%{self._reset()} | "
                      f"Mem: {mem_color}{mem:5.1f}%{self._reset()} | "
                      f"Disk: {disk_color}{disk:5.1f}%{self._reset()}", end="")
                
                if alerts:
                    print(f" | 🚨 {len(alerts)} alerts", end="")
                
                print("", end="\r")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n✅ Monitoring stopped")
    
    def do_heal(self, arg):
        """Auto-heal system issues: heal [memory|disk|process|system]"""
        self.command_count += 1
        
        if not HEALER_AVAILABLE or not self.healer:
            print("Auto-healer module not available. Install core.actuators.auto_healer")
            return
        
        issue_type = arg.strip() if arg else None
        
        if issue_type and issue_type not in ['memory', 'disk', 'process', 'system', 'all']:
            print(f"Unknown issue type: {issue_type}")
            print("Available: memory, disk, process, system, all")
            return
        
        print(f"\n🩺 Running auto-heal{' for ' + issue_type if issue_type else ' for all issues'}...")
        print("-" * 50)
        
        fixes = self.healer.heal(issue_type if issue_type != 'all' else None)
        
        if fixes:
            successful = [f for f in fixes if f['success']]
            failed = [f for f in fixes if not f['success']]
            
            if successful:
                print(f"\n✅ Successful fixes ({len(successful)}):")
                for fix in successful:
                    print(f"  • {fix['action']}: {fix['result']}")
            
            if failed:
                print(f"\n❌ Failed fixes ({len(failed)}):")
                for fix in failed:
                    print(f"  • {fix['action']}: {fix['result']}")
            
            # Save to history
            if hasattr(self.healer, 'healing_history'):
                print(f"\n📝 Healing recorded in history")
        else:
            print("\n✅ No fixes needed - system is healthy!")
    
    def do_predict(self, arg):
        """Show predictions for system issues"""
        self.command_count += 1
        
        print(f"\n🔮 SYSTEM PREDICTIONS")
        print(f"{'='*50}")
        
        # CPU Prediction
        cpu = psutil.cpu_percent(interval=1)
        cpu_history = []
        for _ in range(5):
            cpu_history.append(psutil.cpu_percent(interval=0.2))
        
        cpu_trend = cpu_history[-1] - cpu_history[0]
        
        print(f"\n CPU:")
        print(f"  Current: {cpu:.1f}%")
        if cpu_trend > 5:
            print(f"  ⚠️  CPU usage increasing rapidly (+{cpu_trend:.1f}%)")
            if cpu > 80:
                hours_to_full = (100 - cpu) / (cpu_trend * 12)
                if hours_to_full < 1:
                    print(f"   CRITICAL: CPU saturation in < 1 hour")
                else:
                    print(f"   Warning: CPU saturation in ~{hours_to_full:.1f} hours")
        elif cpu > 80:
            print(f"   Warning: High CPU usage")
        else:
            print(f"   CPU trend stable")
        
        # Memory Prediction
        mem = psutil.virtual_memory()
        print(f"\n Memory:")
        print(f"  Current: {mem.percent:.1f}%")
        
        if mem.percent > 85:
            hours_to_oom = (95 - mem.percent) * 2
            if hours_to_oom < 2:
                print(f"   CRITICAL: OOM risk in < 2 hours")
            elif hours_to_oom < 8:
                print(f"   Warning: OOM risk in ~{hours_to_oom:.1f} hours")
            else:
                print(f"   Warning: High memory usage")
        else:
            print(f"   Memory stable")
        
        # Disk Prediction
        disk = psutil.disk_usage('/')
        print(f"\n Disk:")
        print(f"  Current: {disk.percent:.1f}%")
        
        if disk.percent > 85:
            days_to_full = (100 - disk.percent) * 30
            if days_to_full < 7:
                print(f"   CRITICAL: Disk full in < {days_to_full:.0f} days")
            elif days_to_full < 30:
                print(f"   Warning: Disk full in ~{days_to_full:.0f} days")
            else:
                print(f"   Warning: High disk usage")
        else:
            print(f"   Disk space sufficient")
        
        # Uptime recommendation
        uptime_days = (time.time() - psutil.boot_time()) / 86400
        print(f"\nSystem:")
        print(f"  Uptime: {uptime_days:.1f} days")
        if uptime_days > 30:
            print(f"   Recommendation: Reboot system (uptime > 30 days)")
        elif uptime_days > 14:
            print(f"   Consider rebooting soon")
    
    def do_dashboard(self, arg):
        """Launch the beautiful live dashboard"""
        self.command_count += 1
        
        print("\n Launching Mimir Dashboard...")
        print("Press Ctrl+C to return to CLI\n")
        time.sleep(1)
        
        try:
            from interface.dashboard.live_dashboard import main as dashboard_main
            dashboard_main()
        except ImportError as e:
            print(f" Dashboard not available: {e}")
            print("Installing dashboard dependencies...")
            import subprocess
            subprocess.run(['pip', 'install', 'rich'], cwd=Path.home() / ".mimir/source")
            print("Please restart Mimir and try again.")
        except Exception as e:
            print(f" Dashboard error: {e}")
    
    def do_uptime(self, arg):
        """Show system uptime"""
        uptime_seconds = time.time() - psutil.boot_time()
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        seconds = int(uptime_seconds % 60)
        
        boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"\n System Uptime:")
        print(f"  Running: {days}d {hours}h {minutes}m {seconds}s")
        print(f"  Since: {boot_time}")
    
    def do_users(self, arg):
        """Show logged-in users"""
        users = psutil.users()
        
        if users:
            print(f"\n Logged-in Users:")
            for user in users:
                print(f"  • {user.name} on {user.terminal} since {datetime.fromtimestamp(user.started).strftime('%H:%M:%S')}")
        else:
            print("\n No other users logged in")
    
    def do_ask(self, arg):
        """Ask Mimir a question in natural language"""
        self.command_count += 1
        
        if not arg:
            print("Please ask a question. Example: 'ask why is my system slow?'")
            return
        
        print("\n Thinking...")
        time.sleep(0.5)
        
        query = arg.lower()
        
        if "slow" in query or "performance" in query or "lag" in query:
            cpu = psutil.cpu_percent(interval=2)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            print("\n Performance Analysis:")
            issues = []
            
            if cpu > 70:
                issues.append(f"• High CPU usage: {cpu}%")
                issues.append("  → Check 'top' for CPU hogs")
            if mem.percent > 80:
                issues.append(f"• High memory usage: {mem.percent}%")
                issues.append("  → Clear cache: sync && echo 3 > /proc/sys/vm/drop_caches")
            if disk.percent > 85:
                issues.append(f"• Low disk space: {disk.percent}%")
                issues.append("  → Clean up: sudo apt clean")
            
            if issues:
                print("\n".join(issues))
            else:
                print(" System performance looks normal")
        
        elif "memory" in query or "ram" in query:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            print(f"\n Memory Status:")
            print(f"  Used: {mem.used/1024**3:.1f}GB / {mem.total/1024**3:.1f}GB ({mem.percent}%)")
            print(f"  Available: {mem.available/1024**3:.1f}GB")
            print(f"  Swap: {swap.used/1024**3:.1f}GB / {swap.total/1024**3:.1f}GB ({swap.percent}%)")
        
        elif "disk" in query or "space" in query or "storage" in query:
            disk = psutil.disk_usage('/')
            
            print(f"\n Disk Status:")
            print(f"  Used: {disk.used/1024**3:.1f}GB / {disk.total/1024**3:.1f}GB ({disk.percent}%)")
            print(f"  Free: {disk.free/1024**3:.1f}GB")
        
        elif "cpu" in query or "processor" in query:
            cpu = psutil.cpu_percent(interval=1)
            cores = psutil.cpu_count()
            freq = psutil.cpu_freq()
            
            print(f"\n CPU Status:")
            print(f"  Usage: {cpu}%")
            print(f"  Cores: {cores} logical, {psutil.cpu_count(logical=False)} physical")
            if freq:
                print(f"  Frequency: {freq.current:.0f} MHz")
        
        elif "network" in query or "internet" in query:
            net = psutil.net_io_counters()
            connections = psutil.net_connections()
            
            print(f"\n Network Status:")
            print(f"  Sent: {net.bytes_sent/1024**2:.1f} MB")
            print(f"  Received: {net.bytes_recv/1024**2:.1f} MB")
            print(f"  Connections: {len(connections)}")
        
        else:
            print(f"\n I can help with questions about: performance, memory, disk, cpu, network")
    
    # ==================== EXIT COMMANDS ====================
    
    def do_quit(self, arg):
        """Exit Mimir"""
        print(f"\nGoodbye! You ran {self.command_count} commands this session. 👋")
        return True
    
    def do_exit(self, arg):
        """Exit Mimir"""
        return self.do_quit(arg)
    
    def do_q(self, arg):
        """Quick exit"""
        return self.do_quit(arg)
    
    def do_bye(self, arg):
        """Exit Mimir"""
        return self.do_quit(arg)
    
    # ==================== HELP COMMAND ====================
    
    def do_help(self, arg):
        """Show help information"""
        print("""
╔══════════════════════════════════════════════════════════╗
║                   MIMIR COMMANDS                         ║
╚══════════════════════════════════════════════════════════╝

 BASIC COMMANDS:
  status        - Show comprehensive system status
  uptime        - Show system uptime
  users         - Show logged-in users

 PROCESS COMMANDS:
  top [n]       - Show top n processes (default: 10)
  memory        - Show detailed memory information
  disk          - Show disk usage for all partitions
  network       - Show network statistics

 HEALTH & ALERTS:
  health        - Show system health score
  alerts        - Show active alerts
  alerts history- Show alert history
  monitor [sec] - Start continuous monitoring

 PREDICTIONS & HEALING:
  predict       - Show predictions for system issues
  heal          - Auto-heal all issues
  heal memory   - Fix memory issues
  heal disk     - Fix disk issues  
  heal process  - Fix process issues

 VISUALIZATION:
  dashboard     - Launch beautiful live dashboard

 AI FEATURES:
  copilot       - Enter copilot mode for AI assistance
  web           - Launch web-based interface in browser
  ask <question>- Ask Mimir in plain English

 EXIT:
  quit / exit   - Exit Mimir
  q / bye       - Quick exit

For command-specific help, type: help <command>
Example: help status
""")
    
    def emptyline(self):
        """Do nothing on empty line"""
        pass

def main():
    """Main entry point for CLI"""
    try:
        cli = MimirCLI()
        cli.cmdloop()
    except KeyboardInterrupt:
        print("\n\nGoodbye! 👋")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
