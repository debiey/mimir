"""AI Copilot Engine with local LLM support and model registry"""
import os
import subprocess
import json
import psutil
import time
import platform
from typing import Optional, Dict, List

try:
    from core.llm.ollama_client import OllamaClient
    from core.llm.model_registry import ModelRegistry, ModelCategory
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

try:
    from core.nlp.nlp_engine import NLPEngine
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False


class AICopilot:
    """AI-powered Linux assistant with optional local LLM"""
    
    def __init__(self, use_llm: bool = False, model: str = "tinyllama"):
        self.use_llm = use_llm
        self.llm = None
        self.model_name = model
        self.context = []
        
        # Initialize NLP engine
        self.nlp = NLPEngine(self) if NLP_AVAILABLE else None
        
        if use_llm and OLLAMA_AVAILABLE:
            try:
                self.llm = OllamaClient(model=model)
                self.model_name = self.llm.model
                print(f"Local LLM initialized with model: {self.model_name}")
            except Exception as e:
                print(f"Warning: Failed to initialize LLM: {e}")
                self.use_llm = False
        
        self.system_info = self._get_system_info()
    
    def _get_system_info(self):
        """Get comprehensive system info for context"""
        return {
            'os': platform.system(),
            'os_version': platform.version(),
            'hostname': platform.node(),
            'cpu_count': psutil.cpu_count(),
            'memory_gb': psutil.virtual_memory().total / 1024**3,
            'python': platform.python_version()
        }
    
    def _get_system_prompt(self) -> str:
        """Get system prompt with context"""
        return f"""You are Mimir, an intelligent Linux assistant integrated directly into the system.
You have real-time access to system information and can suggest commands.

Current system context:
- OS: {self.system_info['os']} {self.system_info['os_version']}
- Hostname: {self.system_info['hostname']}
- CPU cores: {self.system_info['cpu_count']}
- RAM: {self.system_info['memory_gb']:.1f} GB
- Python: {self.system_info['python']}
- Current model: {self.model_name}

Guidelines:
1. Be concise but thorough
2. When suggesting commands, explain what they do
3. If asked about system issues, use the actual metrics
4. For dangerous commands (rm -rf, dd, etc.), include a warning
5. Prioritize safety and suggest backups when appropriate
6. If you don't know something, say so honestly
7. Keep responses under 500 words unless the user asks for detail"""
    
    def understand(self, query: str) -> str:
        """Process natural language query - uses LLM or NLP engine"""
        # First try NLP intent recognition
        if self.nlp:
            intent, response = self.nlp.understand(query)
            if response:
                return response
        
        # If NLP didn't match or LLM is enabled, use LLM
        if self.use_llm and self.llm:
            try:
                return self.llm.chat(query, system_prompt=self._get_system_prompt())
            except Exception as e:
                return f"LLM error: {e}. Falling back to rule-based."
        
        # Fallback to rule-based
        return self._rule_based_understand(query)
    
    def _rule_based_understand(self, query: str) -> str:
        """Fallback rule-based understanding"""
        q = query.lower()
        
        if 'slow' in q or 'performance' in q:
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            
            issues = []
            if cpu > 80:
                issues.append(f"High CPU: {cpu}%")
            if mem > 80:
                issues.append(f"High Memory: {mem}%")
            if disk > 85:
                issues.append(f"Low Disk: {disk}%")
            
            if issues:
                return f"⚠️ Issues detected:\n- " + "\n- ".join(issues) + "\n\nTry 'heal' to fix automatically."
            return "✅ System performance looks normal. Check 'top' for process details."
        
        elif 'memory' in q or 'ram' in q:
            mem = psutil.virtual_memory()
            return f"💾 Memory: {mem.percent}% used ({mem.used/1024**3:.1f}/{mem.total/1024**3:.1f} GB)"
        
        elif 'disk' in q or 'space' in q:
            disk = psutil.disk_usage('/')
            return f"💽 Disk: {disk.percent}% used ({disk.used/1024**3:.1f}/{disk.total/1024**3:.1f} GB)"
        
        elif 'cpu' in q:
            cpu = psutil.cpu_percent()
            cores = psutil.cpu_count()
            return f"🔥 CPU: {cpu}% ({cores} cores)"
        
        elif 'network' in q:
            net = psutil.net_io_counters()
            return f"🌐 Network: Sent {net.bytes_sent/1024**2:.1f}MB, Received {net.bytes_recv/1024**2:.1f}MB"
        
        elif 'users' in q:
            users = psutil.users()
            return f"👥 Logged-in users: {', '.join([u.name for u in users])}"
        
        elif 'uptime' in q:
            uptime = time.time() - psutil.boot_time()
            days = int(uptime // 86400)
            hours = int((uptime % 86400) // 3600)
            return f"⏱️ Uptime: {days}d {hours}h"
        
        elif 'find' in q and 'large' in q:
            return "🔍 To find large files:\n   find / -type f -size +100M -ls 2>/dev/null | head -20"
        
        elif 'update' in q or 'upgrade' in q:
            return "📦 To update system:\n   sudo apt update && sudo apt upgrade -y"
        
        else:
            return f"I understand you're asking about '{query}'.\n\nI can help with:\n- System performance ('why slow?')\n- Memory usage\n- Disk space\n- CPU usage\n- Network status\n- Finding large files\n- System updates\n\nTry 'llm on' to enable AI-powered responses!"
    
    def suggest_command(self, task: str) -> dict:
        """Suggest a command for a task"""
        if self.use_llm and self.llm:
            prompt = f"""Suggest a Linux command for: {task}
            
Return in this exact format:
COMMAND: [the command]
EXPLANATION: [brief explanation]
CONFIDENCE: [0-100]"""
            
            try:
                response = self.llm.generate(prompt, system_prompt="You are a Linux expert. Be precise.")
                
                command = ""
                explanation = ""
                confidence = 0.5
                
                for line in response.split('\n'):
                    if line.startswith('COMMAND:'):
                        command = line[8:].strip()
                    elif line.startswith('EXPLANATION:'):
                        explanation = line[12:].strip()
                    elif line.startswith('CONFIDENCE:'):
                        try:
                            confidence = int(line[11:].strip()) / 100
                        except:
                            confidence = 0.7
                
                if command:
                    return {
                        'command': command,
                        'explanation': explanation,
                        'confidence': confidence
                    }
            except:
                pass
        
        # Fallback rule-based suggestions
        suggestions = {
            'find large files': 'find / -type f -size +100M 2>/dev/null | head -20',
            'check disk space': 'df -h',
            'check memory': 'free -h',
            'check processes': 'ps aux --sort=-%cpu | head -20',
            'clean system': 'sudo apt autoremove && sudo apt autoclean',
        }
        
        for key, cmd in suggestions.items():
            if key in task.lower():
                return {
                    'command': cmd,
                    'explanation': f"Runs command to {key}",
                    'confidence': 0.9
                }
        
        return {
            'command': f"man -k {task}",
            'explanation': f"Search man pages for '{task}'",
            'confidence': 0.5
        }
    
    def explain_command(self, command: str) -> dict:
        """Explain what a command does"""
        if self.use_llm and self.llm:
            prompt = f"""Explain this Linux command: {command}
            
Return in this format:
EXPLANATION: [detailed explanation]
EXAMPLES: [1-2 examples]"""
            
            try:
                response = self.llm.generate(prompt)
                
                explanation = ""
                examples = []
                
                for line in response.split('\n'):
                    if line.startswith('EXPLANATION:'):
                        explanation = line[12:].strip()
                    elif line.startswith('EXAMPLES:'):
                        examples = [line[9:].strip()]
                
                if explanation:
                    return {
                        'command': command,
                        'explanation': explanation,
                        'examples': examples
                    }
            except:
                pass
        
        # Fallback explanations
        common = {
            'ls': 'List directory contents',
            'cd': 'Change directory',
            'grep': 'Search for patterns in files',
            'ps': 'Report process status',
            'kill': 'Terminate processes',
            'df': 'Report disk space usage',
            'du': 'Estimate file space usage',
            'free': 'Display memory usage',
        }
        
        base = command.split()[0]
        if base in common:
            return {
                'command': command,
                'explanation': common[base],
                'examples': [f"{base} --help"]
            }
        
        return {
            'command': command,
            'explanation': f"Run 'man {base}' for detailed information",
            'examples': []
        }
    
    def diagnose_issue(self, issue: str) -> dict:
        """Diagnose system issues"""
        if self.use_llm and self.llm:
            prompt = f"""Diagnose this Linux system issue: {issue}
            
Return in this format:
DIAGNOSIS: [list of findings]
SUGGESTIONS: [list of fixes]"""
            
            try:
                response = self.llm.generate(prompt)
                
                diagnosis = []
                suggestions = []
                current = None
                
                for line in response.split('\n'):
                    if line.startswith('DIAGNOSIS:'):
                        current = 'diagnosis'
                    elif line.startswith('SUGGESTIONS:'):
                        current = 'suggestions'
                    elif line.startswith('- ') and current == 'diagnosis':
                        diagnosis.append(line[2:].strip())
                    elif line.startswith('- ') and current == 'suggestions':
                        suggestions.append(line[2:].strip())
                
                if diagnosis or suggestions:
                    return {
                        'issue': issue,
                        'diagnosis': diagnosis,
                        'suggestions': suggestions,
                        'severity': 'warning'
                    }
            except:
                pass
        
        # Fallback
        return {
            'issue': 'General Check',
            'diagnosis': ['System appears operational'],
            'suggestions': ['Run "status" for details', 'Run "health" for health score'],
            'severity': 'info'
        }
    
    def suggest_optimization(self) -> list:
        """Suggest system optimizations"""
        optimizations = []
        
        mem = psutil.virtual_memory()
        if mem.percent > 80:
            optimizations.append({
                'area': 'memory',
                'suggestion': 'Clear memory cache',
                'command': 'sync && echo 3 | sudo tee /proc/sys/vm/drop_caches',
                'benefit': 'Free up RAM'
            })
        
        disk = psutil.disk_usage('/')
        if disk.percent > 80:
            optimizations.append({
                'area': 'disk',
                'suggestion': 'Clean package cache',
                'command': 'sudo apt clean',
                'benefit': 'Free disk space'
            })
        
        return optimizations
