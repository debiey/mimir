"""Advanced Mimir CLI with AI Copilot - Complete Working Version"""
import cmd
import sys
import psutil
import time
import os
import webbrowser
import threading
import subprocess
import requests
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import Mimir modules
try:
    from core.copilot.ai_engine import AICopilot
    COPILOT_AVAILABLE = True
except ImportError:
    COPILOT_AVAILABLE = False

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
    from core.llm.model_registry import ModelRegistry, ModelCategory
    MODEL_REGISTRY_AVAILABLE = True
except ImportError:
    MODEL_REGISTRY_AVAILABLE = False


class AdvancedMimirCLI(cmd.Cmd):
    """Advanced Mimir CLI with AI Copilot and Enhanced Shell"""
    
    intro = """
+======================================================================+
|                    M I M I R   v4.0                                 |
|         Advanced Linux Companion with AI Copilot                    |
+----------------------------------------------------------------------+
|  Type 'help' for commands  |  'llm on' for AI mode                  |
|  Type 'ask' for questions  |  'dashboard' for live view             |
|  Type 'shell_mode' for AI shell  |  'model list' for available AI   |
+======================================================================+
"""
    prompt = "mimir> "
    use_rawinput = True
    completekey = 'tab'
    
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.command_count = 0
        self.command_history = []
        
        # Initialize modules
        self.health = HealthScore() if HEALTH_AVAILABLE else None
        self.alert_mgr = AlertManager() if ALERTS_AVAILABLE else None
        self.healer = AutoHealer() if HEALER_AVAILABLE else None
        
        # Initialize AI Copilot with LLM disabled by default
        self.copilot = None
        if COPILOT_AVAILABLE:
            try:
                self.copilot = AICopilot(use_llm=False)
            except Exception as e:
                print(f"Warning: Failed to initialize AI Copilot: {e}")
    
    # ==================== HELPER METHODS ====================
    
    def _get_color(self, value, warn, crit):
        if value >= crit:
            return '\033[91m'
        elif value >= warn:
            return '\033[93m'
        else:
            return '\033[92m'
    
    def _reset(self):
        return '\033[0m'
    
    # ==================== AI/LLM COMMANDS ====================
    
    def do_llm(self, arg):
        """Toggle local LLM mode: llm on | off | status"""
        if not self.copilot:
            print("Error: AI Copilot not available")
            return
        
        if not arg:
            print(f"Current LLM mode: {'ON' if self.copilot.use_llm else 'OFF'}")
            print("Usage: llm on | off | status")
            return
        
        if arg == "on":
            if not self.copilot.use_llm:
                print("Enabling LLM mode... (first response may take 30-60 seconds)")
                try:
                    self.copilot = AICopilot(use_llm=True, model="tinyllama")
                    print("Local LLM mode ENABLED (using tinyllama)")
                except Exception as e:
                    print(f"Failed to enable LLM: {e}")
        elif arg == "off":
            if self.copilot.use_llm:
                self.copilot = AICopilot(use_llm=False)
                print("Local LLM mode DISABLED")
        elif arg == "status":
            print(f"LLM Mode: {'ON' if self.copilot.use_llm else 'OFF'}")
            if self.copilot.use_llm and hasattr(self.copilot, 'llm') and self.copilot.llm:
                print(f"Model: {self.copilot.llm.model}")
        else:
            print("Usage: llm on | off | status")
    
    def do_ask(self, arg):
        """Ask Mimir a question (uses AI if llm is on)"""
        if not arg:
            print("Usage: ask <question>")
            return
        
        print("\nThinking...")
        
        if self.copilot:
            try:
                response = self.copilot.understand(arg)
                print(f"\n{response}\n")
            except Exception as e:
                print(f"Error: {e}")
        else:
            print("AI Copilot not available")
    
    # ==================== MODEL MANAGEMENT COMMANDS ====================
    
    def do_model(self, arg):
        """Manage AI models: model <subcommand> [args]"""
        if not arg:
            print("Model Management Commands:")
            print("  model list           - Show all available models with details")
            print("  model installed      - Show installed models")
            print("  model info <name>    - Show detailed info about a model")
            print("  model recommend      - Get model recommendation for your system")
            print("  model pull <name>    - Download a model (shows progress)")
            print("  model remove <name>  - Remove a model")
            print("  model switch <name>  - Switch to a different model")
            print("  model current        - Show current model")
            return
        
        parts = arg.split()
        cmd = parts[0]
        
        if cmd == "list":
            self._model_list()
        elif cmd == "installed":
            self._model_installed()
        elif cmd == "info":
            if len(parts) < 2:
                print("Usage: model info <model_name>")
                return
            self._model_info(parts[1])
        elif cmd == "recommend":
            self._model_recommend()
        elif cmd == "pull":
            if len(parts) < 2:
                print("Usage: model pull <model_name>")
                print("Available: tinyllama, phi, gemma, mistral, llama2, orca-mini, mixtral, llama3, codellama, deepseek-coder")
                return
            self._model_pull(parts[1])
        elif cmd == "remove":
            if len(parts) < 2:
                print("Usage: model remove <model_name>")
                return
            self._model_remove(parts[1])
        elif cmd == "switch":
            if len(parts) < 2:
                print("Usage: model switch <model_name>")
                return
            self._model_switch(parts[1])
        elif cmd == "current":
            self._model_current()
        else:
            print(f"Unknown model command: {cmd}")
            print("Use: list, installed, info, recommend, pull, remove, switch, current")
    
    def _model_list(self):
        """List all available models with details"""
        if not MODEL_REGISTRY_AVAILABLE:
            print("Model registry not available")
            return
        
        print("\n" + "="*80)
        print("AVAILABLE AI MODELS")
        print("="*80)
        
        installed = ModelRegistry.get_installed_models()
        
        for category in [ModelCategory.FAST, ModelCategory.BALANCED, ModelCategory.POWERFUL, ModelCategory.CODING]:
            models = ModelRegistry.get_models_by_category(category)
            if models:
                print(f"\n{category.value.upper()} MODELS:")
                print("-" * 70)
                for model in models:
                    status = "✓" if model.name in installed else "○"
                    status_color = "\033[92m" if model.name in installed else "\033[90m"
                    ram_req = f"({model.recommended_ram_gb}GB RAM)"
                    size_str = f"{model.size_gb:.1f}GB"
                    print(f"  {status_color}{status}{self._reset()} {model.display_name:15} {size_str:>6} {ram_req:>12}")
                    print(f"      {model.description[:60]}")
        
        print("\n" + "="*80)
        if installed:
            print(f"✓ Installed: {', '.join(installed)}")
        else:
            print("○ No models installed. Run: model pull <name>")
    
    def _model_installed(self):
        """Show installed models only"""
        if not MODEL_REGISTRY_AVAILABLE:
            print("Model registry not available")
            return
        
        installed = ModelRegistry.get_installed_models()
        
        if installed:
            print("\nInstalled Models:")
            print("-" * 40)
            for name in installed:
                model = ModelRegistry.get_model(name)
                if model:
                    print(f"  ✓ {model.display_name:15} - {model.size_gb:.1f}GB - {model.category.value}")
                else:
                    print(f"  ✓ {name}")
        else:
            print("\nNo models installed.")
            print("Run: model pull tinyllama")
    
    def _model_info(self, model_name):
        """Show detailed info about a specific model"""
        if not MODEL_REGISTRY_AVAILABLE:
            print("Model registry not available")
            return
        
        model = ModelRegistry.get_model(model_name)
        if not model:
            print(f"Model '{model_name}' not found.")
            print("Use 'model list' to see available models.")
            return
        
        installed = ModelRegistry.get_installed_models()
        is_installed = model.name in installed
        
        print(f"\n{'='*60}")
        print(f"MODEL: {model.display_name} ({model.name})")
        print(f"{'='*60}")
        print(f"Category:    {model.category.value}")
        print(f"Size:        {model.size_gb:.1f} GB")
        print(f"RAM Required: {model.recommended_ram_gb} GB")
        print(f"Description: {model.description}")
        print(f"\nUse Cases:")
        for use_case in model.use_cases:
            print(f"  • {use_case}")
        
        if is_installed:
            print(f"\nStatus: ✓ INSTALLED")
            print(f"To use: model switch {model.name}")
        else:
            print(f"\nStatus: ○ NOT INSTALLED")
            print(f"To install: model pull {model.name}")
    
    def _model_recommend(self):
        """Get model recommendation based on system RAM"""
        if not MODEL_REGISTRY_AVAILABLE:
            print("Model registry not available")
            return
        
        ram_gb = psutil.virtual_memory().total / 1024**3
        recommended = ModelRegistry.recommend_model(ram_gb)
        model = ModelRegistry.get_model(recommended)
        
        print(f"\nSystem RAM: {ram_gb:.1f} GB")
        print(f"\nRecommended Model: {model.display_name}")
        print(f"  Size: {model.size_gb:.1f} GB")
        print(f"  Category: {model.category.value}")
        print(f"  Description: {model.description}")
        print(f"\nTo install: model pull {recommended}")
        
        print("\nAlternative options based on your RAM:")
        if ram_gb >= 8:
            print("  • mixtral - Best quality (needs 8GB+)")
            print("  • llama3 - Latest model (needs 6GB+)")
        elif ram_gb >= 4:
            print("  • mistral - Excellent all-rounder (needs 4GB)")
            print("  • codellama - Great for coding (needs 4GB)")
        else:
            print("  • phi - Good balance (needs 2GB)")
            print("  • tinyllama - Fastest option (needs 1GB)")
    
    def _model_pull(self, model_name):
        """Download a model with real-time progress display"""
        if not MODEL_REGISTRY_AVAILABLE:
            print("Model registry not available")
            return
        
        model = ModelRegistry.get_model(model_name)
        if not model:
            print(f"Model '{model_name}' not found in registry.")
            print("Available models: tinyllama, phi, gemma, mistral, llama2, orca-mini, mixtral, llama3, codellama, deepseek-coder")
            return
        
        # Check if already installed
        installed = ModelRegistry.get_installed_models()
        if model_name in installed:
            print(f"\nModel {model.display_name} is already installed.")
            print(f"To use it: model switch {model_name}")
            return
        
        print(f"\n" + "="*60)
        print(f"DOWNLOADING: {model.display_name}")
        print(f"Size: {model.size_gb:.1f} GB")
        print(f"Estimated time: {int(model.size_gb * 5)}-{int(model.size_gb * 10)} minutes")
        print("="*60)
        print("\nProgress will show below. This may take a while...\n")
        
        try:
            # Run ollama pull and show real-time output
            process = subprocess.Popen(
                ['ollama', 'pull', model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Read and display each line as it comes
            for line in process.stdout:
                # Clean up the line and print
                line = line.strip()
                if line:
                    print(line)
            
            process.wait()
            
            if process.returncode == 0:
                print(f"\n" + "="*60)
                print(f"✓ SUCCESS: {model.display_name} downloaded successfully!")
                print(f"  Size: {model.size_gb:.1f} GB")
                print(f"  To use it: model switch {model_name}")
                print("="*60)
                
                # Refresh installed models list
                if MODEL_REGISTRY_AVAILABLE:
                    ModelRegistry.get_installed_models.cache_clear()
            else:
                print(f"\n✗ FAILED: Could not download {model.display_name}")
                print("  Check your internet connection and try again.")
                
        except FileNotFoundError:
            print("\n✗ ERROR: Ollama not found!")
            print("  Please install Ollama first: curl -fsSL https://ollama.com/install.sh | sh")
        except Exception as e:
            print(f"\n✗ ERROR: {e}")
    
    def _model_remove(self, model_name):
        """Remove a model"""
        if not MODEL_REGISTRY_AVAILABLE:
            print("Model registry not available")
            return
        
        installed = ModelRegistry.get_installed_models()
        if model_name not in installed:
            print(f"Model '{model_name}' is not installed.")
            return
        
        model = ModelRegistry.get_model(model_name)
        display_name = model.display_name if model else model_name
        
        print(f"\nRemove {display_name}?")
        confirm = input("Are you sure? (y/N): ")
        if confirm.lower() != 'y':
            print("Cancelled.")
            return
        
        try:
            process = subprocess.Popen(
                ['ollama', 'rm', model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            for line in process.stdout:
                print(line.strip())
            
            process.wait()
            
            if process.returncode == 0:
                print(f"✓ Model {display_name} removed")
                if self.copilot and self.copilot.use_llm and hasattr(self.copilot, 'llm') and self.copilot.llm.model == model_name:
                    print("Note: This was your active model. LLM mode has been disabled.")
                    self.copilot = AICopilot(use_llm=False)
            else:
                print(f"✗ Failed to remove")
        except Exception as e:
            print(f"Error: {e}")
    
    def _model_switch(self, model_name):
        """Switch to a different model"""
        if not self.copilot:
            print("AI Copilot not initialized")
            return
        
        if not MODEL_REGISTRY_AVAILABLE:
            print("Model registry not available")
            return
        
        installed = ModelRegistry.get_installed_models()
        if model_name not in installed:
            print(f"Model '{model_name}' is not installed.")
            print(f"Installed: {', '.join(installed) if installed else 'None'}")
            print(f"To install: model pull {model_name}")
            return
        
        model = ModelRegistry.get_model(model_name)
        display_name = model.display_name if model else model_name
        
        print(f"Switching to {display_name}...")
        try:
            self.copilot = AICopilot(use_llm=True, model=model_name)
            print(f"✓ Switched to model: {display_name}")
        except Exception as e:
            print(f"Failed to switch model: {e}")
    
    def _model_current(self):
        """Show current model"""
        if not self.copilot:
            print("AI Copilot not initialized")
            return
        
        if self.copilot.use_llm and hasattr(self.copilot, 'llm') and self.copilot.llm:
            current_model = self.copilot.llm.model
            if MODEL_REGISTRY_AVAILABLE:
                model = ModelRegistry.get_model(current_model)
                if model:
                    print(f"\nCurrent Model: {model.display_name} ({model.name})")
                    print(f"Category: {model.category.value}")
                    print(f"Size: {model.size_gb:.1f} GB")
                else:
                    print(f"Current Model: {current_model}")
            else:
                print(f"Current Model: {current_model}")
        else:
            print("LLM mode is disabled. Run 'llm on' to enable.")
    
    def do_llm_test(self, arg):
        """Test Ollama connection and model response"""
        print("\nTesting Ollama connection...")
        print("-" * 40)
        
        try:
            start = time.time()
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            elapsed = time.time() - start
            if response.status_code == 200:
                models = response.json().get('models', [])
                print(f"✓ Ollama is running ({elapsed:.2f}s)")
                if models:
                    print(f"   Models: {[m['name'] for m in models]}")
                else:
                    print("   No models found. Run: model pull tinyllama")
                
                if self.copilot and self.copilot.use_llm and self.copilot.llm:
                    print("\nTesting model response...")
                    test_start = time.time()
                    try:
                        test_response = requests.post(
                            "http://localhost:11434/api/generate",
                            json={
                                "model": self.copilot.llm.model,
                                "prompt": "Say 'OK'",
                                "stream": False
                            },
                            timeout=60
                        )
                        test_elapsed = time.time() - test_start
                        if test_response.status_code == 200:
                            print(f"✓ Model responded in {test_elapsed:.2f}s")
                        else:
                            print(f"⚠️ Model test returned: {test_response.status_code}")
                    except requests.exceptions.Timeout:
                        print("⚠️ Model test timed out after 60 seconds")
            else:
                print(f"⚠️ Ollama returned status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ Ollama is not running. Start with: ollama serve")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # ==================== SYSTEM COMMANDS ====================
    
    def do_status(self, arg):
        """Show system status"""
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        net = psutil.net_io_counters()
        processes = len(psutil.pids())
        uptime = time.time() - psutil.boot_time()
        days = int(uptime // 86400)
        hours = int((uptime % 86400) // 3600)
        
        print(f"\n{'='*50}")
        print(f"SYSTEM STATUS - {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*50}")
        
        cpu_color = self._get_color(cpu, 70, 90)
        print(f"CPU:     {cpu_color}{cpu:6.1f}%{self._reset()}")
        
        mem_color = self._get_color(mem.percent, 80, 95)
        print(f"Memory:  {mem_color}{mem.percent:6.1f}%{self._reset()} ({mem.used/1024**3:.1f}/{mem.total/1024**3:.1f} GB)")
        
        disk_color = self._get_color(disk.percent, 80, 95)
        print(f"Disk:    {disk_color}{disk.percent:6.1f}%{self._reset()} ({disk.used/1024**3:.1f}/{disk.total/1024**3:.1f} GB)")
        
        print(f"Network: Sent {net.bytes_sent/1024**2:.1f}MB, Recv {net.bytes_recv/1024**2:.1f}MB")
        print(f"System:  Processes: {processes} | Uptime: {days}d {hours}h")
        
        if self.health:
            score = self.health.get_score()
            print(f"Health Score: {score:.1f}/100")
        
        print(f"{'='*50}")
    
    def do_health(self, arg):
        """Show health score"""
        if self.health:
            score = self.health.get_score()
            print(f"\nHealth Score: {score:.1f}/100")
        else:
            print("Health module not available")
    
    def do_memory(self, arg):
        """Show memory info"""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        print(f"\nMEMORY")
        print(f"  RAM:    {mem.percent}% ({mem.used/1024**3:.1f}/{mem.total/1024**3:.1f} GB)")
        print(f"  Swap:   {swap.percent}% ({swap.used/1024**3:.1f}/{swap.total/1024**3:.1f} GB)")
    
    def do_disk(self, arg):
        """Show disk usage"""
        disk = psutil.disk_usage('/')
        print(f"\nDISK")
        print(f"  Used: {disk.percent}% ({disk.used/1024**3:.1f}/{disk.total/1024**3:.1f} GB)")
        print(f"  Free: {disk.free/1024**3:.1f} GB")
    
    def do_network(self, arg):
        """Show network info"""
        net = psutil.net_io_counters()
        print(f"\nNETWORK")
        print(f"  Sent:     {net.bytes_sent/1024**2:.1f} MB")
        print(f"  Received: {net.bytes_recv/1024**2:.1f} MB")
    
    def do_top(self, arg):
        """Show top processes"""
        n = 10
        if arg and arg.isdigit():
            n = int(arg)
        
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                if proc.info['cpu_percent'] > 0:
                    processes.append(proc.info)
            except:
                pass
        
        processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        print(f"\nTOP {n} PROCESSES BY CPU")
        print("-" * 50)
        for proc in processes[:n]:
            print(f"{proc['pid']:6d} {proc['cpu_percent']:6.1f}%  {proc['name'][:40]}")
    
    def do_users(self, arg):
        """Show logged-in users"""
        users = psutil.users()
        if users:
            print(f"\nLogged-in Users:")
            for user in users:
                print(f"  * {user.name} on {user.terminal}")
        else:
            print("\nNo other users logged in")
    
    def do_uptime(self, arg):
        """Show system uptime"""
        uptime = time.time() - psutil.boot_time()
        days = int(uptime // 86400)
        hours = int((uptime % 86400) // 3600)
        minutes = int((uptime % 3600) // 60)
        print(f"\nUptime: {days}d {hours}h {minutes}m")
    
    # ==================== PREDICTIONS ====================
    
    def do_predict(self, arg):
        """Show predictive analytics"""
        print("\nPREDICTIONS")
        print("-" * 40)
        
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        
        print(f"CPU:    {cpu:.1f}%")
        if cpu > 80:
            print("  WARNING: High CPU - may cause slowdown")
        print(f"Memory: {mem:.1f}%")
        if mem > 85:
            print("  WARNING: High memory - OOM risk")
        print(f"Disk:   {disk:.1f}%")
        if disk > 85:
            print("  WARNING: Low disk space")
    
    # ==================== AUTO-HEALING ====================
    
    def do_heal(self, arg):
        """Auto-heal issues: heal [memory|disk]"""
        if not self.healer:
            print("Auto-healer not available")
            return
        
        issue = arg.strip() if arg else "all"
        print(f"\nHealing {issue} issues...")
        
        if issue == "memory":
            fixes = self.healer._fix_memory()
        elif issue == "disk":
            fixes = self.healer._fix_disk()
        elif issue == "all":
            fixes = self.healer.heal()
        else:
            print("Usage: heal memory | disk | all")
            return
        
        if fixes:
            for fix in fixes:
                if fix['success']:
                    print(f"  [OK] {fix['action']}: {fix['result']}")
        else:
            print("  No issues found")
    
    def do_heal_status(self, arg):
        """Show healing status"""
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        print("\nHEALTH STATUS")
        print("-" * 30)
        status_mem = "HIGH" if mem.percent > 80 else "OK"
        status_disk = "HIGH" if disk.percent > 80 else "OK"
        print(f"Memory: {mem.percent}% [{status_mem}]")
        print(f"Disk:   {disk.percent}% [{status_disk}]")
    
    def do_kill(self, arg):
        """Kill a process by PID"""
        if not arg or not arg.isdigit():
            print("Usage: kill <PID>")
            return
        
        pid = int(arg)
        try:
            proc = psutil.Process(pid)
            name = proc.name()
            confirm = input(f"Kill {name} (PID: {pid})? (y/N): ")
            if confirm.lower() == 'y':
                proc.terminate()
                print(f"Process {pid} terminated")
        except psutil.NoSuchProcess:
            print(f"Process {pid} not found")
    
    # ==================== COMMAND EXECUTION ====================
    
    def do_shell(self, arg):
        """Run a shell command"""
        if not arg:
            print("Usage: shell <command> or ! <command>")
            return
        
        self._run_command(arg)
    
    def _run_command(self, command):
        """Execute a command"""
        self.command_history.append(command)
        print(f"\nExecuting: {command}")
        print("-" * 40)
        
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(f"Errors:\n{result.stderr}")
            print(f"\nExit code: {result.returncode}")
        except subprocess.TimeoutExpired:
            print("Command timed out")
        except Exception as e:
            print(f"Error: {e}")
    
    def do_history(self, arg):
        """Show command history"""
        if not self.command_history:
            print("No command history")
            return
        
        print("\nCOMMAND HISTORY")
        for i, cmd in enumerate(self.command_history[-20:], 1):
            print(f"{i:2d}. {cmd}")
    
    # ==================== ENHANCED SHELL MODE ====================
    
    def do_shell_mode(self, arg):
        """Launch AI-powered shell with command suggestions"""
        print("\nLaunching Mimir AI Shell...")
        print("  Features: AI suggestions for unknown commands")
        print("  Type 'exit' to return\n")
        
        shell_script = Path(__file__).parent.parent.parent / "scripts" / "mimir-shell.sh"
        
        if not shell_script.exists():
            shell_script.parent.mkdir(parents=True, exist_ok=True)
            content = (
                '#!/bin/bash\n'
                '# Mimir Shell - AI-powered command assistant\n'
                '\n'
                'MIMIR_DIR="/home/chioma/.mimir/source"\n'
                '\n'
                '# Colors\n'
                'RED=\'\\033[0;31m\'\n'
                'GREEN=\'\\033[0;32m\'\n'
                'YELLOW=\'\\033[1;33m\'\n'
                'NC=\'\\033[0m\'\n'
                '\n'
                '# Set prompt\n'
                'PS1=\'\\u@\\h:\\w [Mimir] \\$ \'\n'
                '\n'
                '# AI suggestion function\n'
                'mimir_suggest() {\n'
                '    local cmd="$1"\n'
                '    cd "$MIMIR_DIR" && source venv/bin/activate 2>/dev/null && python3 -c "\n'
                'import sys\n'
                'sys.path.insert(0, \'$MIMIR_DIR\')\n'
                'try:\n'
                '    from core.copilot.ai_engine import AICopilot\n'
                '    copilot = AICopilot(use_llm=True)\n'
                '    result = copilot.suggest_command(\'$cmd\')\n'
                '    print(result[\'command\'])\n'
                'except Exception:\n'
                '    pass\n'
                '" 2>/dev/null && deactivate 2>/dev/null\n'
                '}\n'
                '\n'
                '# Command not found handler\n'
                'command_not_found_handle() {\n'
                '    local cmd="$1"\n'
                '    echo -e "${RED}Command not found: $cmd${NC}"\n'
                '    echo -e "${YELLOW}AI suggestion:${NC}"\n'
                '    mimir_suggest "$cmd"\n'
                '    return 127\n'
                '}\n'
                '\n'
                '# Welcome message\n'
                'echo ""\n'
                'echo "============================================================\n'
                'echo "                MIMIR AI SHELL"\n'
                'echo "============================================================\n'
                'echo "  Type \'exit\' to return"\n'
                'echo ""\n'
                '\n'
                '# Start shell\n'
                'exec bash --rcfile <(echo "command_not_found_handle() { local cmd=\\"$1\\"; echo -e \\"\\033[0;31mCommand not found: $cmd\\033[0m\\"; cd $MIMIR_DIR && source venv/bin/activate 2>/dev/null && python3 -c \\"import sys; sys.path.insert(0, \'$MIMIR_DIR\'); from core.copilot.ai_engine import AICopilot; copilot = AICopilot(use_llm=True); result = copilot.suggest_command(\'$cmd\'); print(result[\'command\'])\\" 2>/dev/null; deactivate 2>/dev/null; return 127; }")\n'
            )
            shell_script.write_text(content)
            shell_script.chmod(0o755)
        
        try:
            subprocess.run([str(shell_script)])
        except Exception as e:
            print(f"Error: {e}")
    
    def do_shell_integrate(self, arg):
        """Add AI suggestions to your shell permanently"""
        if arg not in ["bashrc", "zshrc"]:
            print("Usage: shell_integrate bashrc | zshrc")
            print("Adds AI-powered command suggestions to your shell")
            return
        
        rc_file = Path.home() / f".{arg}"
        if not rc_file.exists():
            print(f"File not found: {rc_file}")
            return
        
        scripts_dir = Path(__file__).parent.parent.parent / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        
        bashrc_script = scripts_dir / "mimir-bashrc.sh"
        
        if not bashrc_script.exists():
            bashrc_content = (
                '# Mimir Shell Integration\n'
                f'MIMIR_DIR="{Path(__file__).parent.parent.parent}"\n'
                '\n'
                '# AI suggestion function\n'
                'mimir_suggest() {\n'
                '    local cmd="$1"\n'
                '    cd "$MIMIR_DIR" && source venv/bin/activate 2>/dev/null && python3 -c "\n'
                'import sys\n'
                'sys.path.insert(0, \'$MIMIR_DIR\')\n'
                'try:\n'
                '    from core.copilot.ai_engine import AICopilot\n'
                '    copilot = AICopilot(use_llm=True)\n'
                '    result = copilot.suggest_command(\'$cmd\')\n'
                '    print(result[\'command\'])\n'
                'except Exception:\n'
                '    pass\n'
                '" 2>/dev/null && deactivate 2>/dev/null\n'
                '}\n'
                '\n'
                '# Command not found handler\n'
                'command_not_found_handle() {\n'
                '    local cmd="$1"\n'
                '    echo "Command not found: $cmd"\n'
                '    echo "AI suggestion:"\n'
                '    mimir_suggest "$cmd"\n'
                '    return 127\n'
                '}\n'
                '\n'
                '# Aliases\n'
                'alias m=\'cd $MIMIR_DIR && source venv/bin/activate && python3 mimir.py cli\'\n'
                'alias mimir=\'m\'\n'
                '\n'
                'echo "Mimir: Type \'m\' to launch"\n'
            )
            bashrc_script.write_text(bashrc_content)
            bashrc_script.chmod(0o755)
        
        integration_line = f'source {bashrc_script}'
        
        rc_content = rc_file.read_text()
        if integration_line in rc_content:
            print("Shell integration already enabled")
        else:
            with open(rc_file, 'a') as f:
                f.write(f"\n# Mimir Shell Integration\n{integration_line}\n")
            print(f"Integration added to {rc_file}")
            print("  Restart terminal or run: source ~/.bashrc")
            print("  Features: AI suggestions for unknown commands")
            print("  Quick access: 'm' to launch Mimir")
    
    # ==================== VISUALIZATION ====================
    
    def do_dashboard(self, arg):
        """Launch live dashboard"""
        print("\nLaunching Dashboard...")
        try:
            from interface.dashboard.live_dashboard import main as dashboard_main
            dashboard_main()
        except ImportError:
            print("Dashboard not available")
    
    def do_web(self, arg):
        """Launch web interface"""
        print("\nStarting Web Interface...")
        
        def run_server():
            try:
                from interface.web.copilot_web import app
                app.run(host='0.0.0.0', port=5000, debug=False)
            except Exception as e:
                print(f"Web server error: {e}")
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        time.sleep(2)
        webbrowser.open('http://localhost:5000')
        print("   Web interface: http://localhost:5000")
        print("   Press Ctrl+C to return\n")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n   To stop server: pkill -f copilot_web.py")
    
    # ==================== UTILITY ====================
    
    def do_clear(self, arg):
        """Clear screen"""
        os.system('clear')
    
    def do_logs(self, arg):
        """Show logs"""
        log_dir = Path.home() / ".mimir" / "logs"
        if log_dir.exists():
            print("\nLog files:")
            for log in list(log_dir.glob("*.log"))[-5:]:
                print(f"  * {log.name}")
    
    # ==================== HELP ====================
    
    def do_help(self, arg):
        """Show help"""
        print("""
+======================================================================+
|                    MIMIR v4.0 COMMANDS                              |
+======================================================================+

AI FEATURES:
  llm on|off|status  - Enable/disable local LLM
  ask <question>     - Ask Mimir anything
  llm_test           - Test Ollama connection

MODEL MANAGEMENT:
  model list         - Show all available AI models with details
  model installed    - Show installed models
  model info <name>  - Show detailed info about a model
  model recommend    - Get model recommendation for your system
  model pull <name>  - Download a model (shows real-time progress)
  model remove <name>- Remove a model
  model switch <name>- Switch to a different model
  model current      - Show current model

SYSTEM:
  status             - Show system status
  health             - Show health score
  memory             - Show memory info
  disk               - Show disk usage
  network            - Show network stats
  top [n]            - Show top n processes
  users              - Show logged-in users
  uptime             - Show system uptime

PREDICTIONS & HEALING:
  predict            - Show predictions
  heal [memory|disk] - Auto-heal issues
  heal status        - Show healing status
  kill <PID>         - Kill a process

COMMAND EXECUTION:
  ! <command>        - Run shell command
  shell <command>    - Run shell command
  history            - Show command history

SHELL FEATURES:
  shell_mode         - Launch AI-powered shell
  shell_integrate    - Add AI suggestions to .bashrc/.zshrc

VISUALIZATION:
  dashboard          - Live terminal dashboard
  web                - Web interface

UTILITY:
  clear              - Clear screen
  logs               - Show log files

EXIT:
  quit / exit        - Exit Mimir
""")
    
    def do_quit(self, arg):
        """Exit Mimir"""
        print(f"\nGoodbye!")
        return True
    
    def do_exit(self, arg):
        return self.do_quit(arg)
    
    def do_q(self, arg):
        return self.do_quit(arg)
    
    def emptyline(self):
        pass
    
    def default(self, line):
        if line.startswith('!'):
            self._run_command(line[1:])
        else:
            print(f"Unknown command: {line}")
            print("Type 'help' for commands")


def main():
    try:
        cli = AdvancedMimirCLI()
        cli.cmdloop()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
