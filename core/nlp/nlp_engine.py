"""Natural Language Processing enhancements for Mimir"""
import re
import subprocess
import psutil
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class NLPEngine:
    """Enhanced natural language understanding for system commands"""
    
    def __init__(self, copilot=None):
        self.copilot = copilot
        self.intent_patterns = self._build_intent_patterns()
    
    def _build_intent_patterns(self) -> Dict[str, Dict]:
        """Build patterns for intent recognition"""
        return {
            'system_health': {
                'patterns': [
                    r'(how|what).*(health|status|running)',
                    r'(is.*ok|everything.*ok)',
                    r'(check.*system|system.*check)'
                ],
                'handler': self._handle_health_intent
            },
            'performance': {
                'patterns': [
                    r'(why|what).*(slow|fast|performance|lag)',
                    r'(check.*speed|speed.*issue)',
                    r'(system.*slow|slow.*system)'
                ],
                'handler': self._handle_performance_intent
            },
            'memory_usage': {
                'patterns': [
                    r'(memory|ram).*(usage|using|used)',
                    r'(how much.*memory|memory.*left)',
                    r'(free.*ram|ram.*free)'
                ],
                'handler': self._handle_memory_intent
            },
            'disk_space': {
                'patterns': [
                    r'(disk|storage).*(space|full|usage|using)',
                    r'(how much.*space|space.*left)',
                    r'(free.*disk|disk.*free)'
                ],
                'handler': self._handle_disk_intent
            },
            'process_management': {
                'patterns': [
                    r'(kill|stop|end).*(process|program)',
                    r'(what.*running|running.*process)',
                    r'(top.*process|process.*using)'
                ],
                'handler': self._handle_process_intent
            },
            'command_help': {
                'patterns': [
                    r'(how to|how do).*(command|do|run|use)',
                    r'(explain|what does).*(command|do)',
                    r'(help.*with|need.*help)'
                ],
                'handler': self._handle_command_help_intent
            },
            'file_operations': {
                'patterns': [
                    r'(find|search).*(file|directory|folder)',
                    r'(large.*files|files.*large)',
                    r'(delete|remove).*(file|folder)'
                ],
                'handler': self._handle_file_intent
            },
            'network': {
                'patterns': [
                    r'(network|internet|wifi).*(status|connected|speed)',
                    r'(check.*connection|connection.*issue)',
                    r'(ip address|what.*ip)'
                ],
                'handler': self._handle_network_intent
            },
            'updates': {
                'patterns': [
                    r'(update|upgrade).*(system|package|software)',
                    r'(outdated|new version)',
                    r'(check.*update|update.*available)'
                ],
                'handler': self._handle_update_intent
            },
            'security': {
                'patterns': [
                    r'(security|firewall|safe|secure)',
                    r'(hack|vulnerable|breach)',
                    r'(check.*security|security.*check)'
                ],
                'handler': self._handle_security_intent
            }
        }
    
    def understand(self, query: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse natural language query and return intent and entities"""
        query_lower = query.lower()
        
        for intent, data in self.intent_patterns.items():
            for pattern in data['patterns']:
                if re.search(pattern, query_lower):
                    return intent, data['handler'](query)
        
        return None, None
    
    def _handle_health_intent(self, query: str) -> str:
        """Handle system health queries"""
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        response = f"System Health Report:\n"
        response += f"  CPU: {cpu}% {'🟢' if cpu < 70 else '🟡' if cpu < 90 else '🔴'}\n"
        response += f"  Memory: {mem.percent}% {'🟢' if mem.percent < 70 else '🟡' if mem.percent < 90 else '🔴'}\n"
        response += f"  Disk: {disk.percent}% {'🟢' if disk.percent < 70 else '🟡' if disk.percent < 90 else '🔴'}\n"
        
        if cpu > 80 or mem.percent > 80 or disk.percent > 80:
            response += "\n⚠️  Some metrics need attention. Run 'heal' for auto-fixes."
        
        return response
    
    def _handle_performance_intent(self, query: str) -> str:
        """Handle performance-related queries"""
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory()
        processes = []
        
        for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
            try:
                if proc.info['cpu_percent'] > 10:
                    processes.append(proc.info)
            except:
                pass
        
        processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        
        response = "Performance Analysis:\n"
        if cpu > 80:
            response += f"⚠️  High CPU: {cpu}%\n"
        if mem.percent > 80:
            response += f"⚠️  High Memory: {mem.percent}%\n"
        
        if processes:
            response += "\nTop CPU consumers:\n"
            for proc in processes[:3]:
                response += f"  • {proc['name']}: {proc['cpu_percent']:.1f}%\n"
        
        return response
    
    def _handle_memory_intent(self, query: str) -> str:
        """Handle memory-related queries"""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return f"""Memory Status:
  RAM: {mem.percent}% used ({mem.used/1024**3:.1f}/{mem.total/1024**3:.1f} GB)
  Available: {mem.available/1024**3:.1f} GB
  Swap: {swap.percent}% used ({swap.used/1024**3:.1f}/{swap.total/1024**3:.1f} GB)

To free memory: run 'heal memory'"""
    
    def _handle_disk_intent(self, query: str) -> str:
        """Handle disk-related queries"""
        disk = psutil.disk_usage('/')
        
        return f"""Disk Status:
  Used: {disk.percent}% ({disk.used/1024**3:.1f}/{disk.total/1024**3:.1f} GB)
  Free: {disk.free/1024**3:.1f} GB

To clean disk space: run 'heal disk'"""
    
    def _handle_process_intent(self, query: str) -> str:
        """Handle process-related queries"""
        if 'kill' in query.lower() or 'stop' in query.lower():
            return "To kill a process:\n  1. Find PID with 'top' or 'ps aux'\n  2. Run: kill <PID>"
        else:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    processes.append(proc.info)
                except:
                    pass
            processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
            
            response = "Top 5 processes:\n"
            for proc in processes[:5]:
                response += f"  {proc['pid']:6d} {proc['cpu_percent']:6.1f}%  {proc['name']}\n"
            return response
    
    def _handle_command_help_intent(self, query: str) -> str:
        """Handle command help queries"""
        # Extract command from query
        words = query.split()
        for word in words:
            if word in ['ls', 'cd', 'grep', 'ps', 'kill', 'df', 'du', 'top', 'find']:
                return self._get_command_help(word)
        
        return "I can help with common Linux commands. Try asking about: ls, cd, grep, ps, kill, df, du, top, find"
    
    def _get_command_help(self, cmd: str) -> str:
        """Get help for specific command"""
        help_texts = {
            'ls': "List directory contents\n  ls -la    Show all files with details\n  ls *.txt  List only text files",
            'cd': "Change directory\n  cd /path   Go to path\n  cd ..      Go up one level\n  cd ~       Go home",
            'grep': "Search for patterns\n  grep 'text' file.txt\n  grep -r 'pattern' .   Search recursively",
            'ps': "Process status\n  ps aux     Show all processes\n  ps aux --sort=-%cpu  Sort by CPU",
            'kill': "Terminate processes\n  kill PID    Terminate process\n  kill -9 PID Force kill",
            'df': "Disk free\n  df -h      Human-readable disk usage\n  df -h /    Check root partition",
            'du': "Disk usage\n  du -sh *   Size of all files/folders\n  du -h --max-depth=1",
            'top': "Process monitor\n  top        Interactive view\n  q          Quit",
            'find': "Search for files\n  find . -name '*.txt'\n  find / -size +100M  Large files",
        }
        return help_texts.get(cmd, f"Run 'man {cmd}' for detailed help")
    
    def _handle_file_intent(self, query: str) -> str:
        """Handle file operation queries"""
        if 'large' in query.lower():
            return "To find large files:\n  find / -type f -size +100M -ls 2>/dev/null | head -20"
        elif 'find' in query.lower():
            return "To find files:\n  find /path -name 'filename' 2>/dev/null"
        else:
            return "File operations:\n  ls -la        List files\n  find . -name   Search files\n  du -sh *       Show sizes"
    
    def _handle_network_intent(self, query: str) -> str:
        """Handle network queries"""
        return """Network Commands:
  Check IP: ip addr show
  Test connection: ping google.com
  Show connections: netstat -tulpn
  Monitor traffic: iftop (install first)"""
    
    def _handle_update_intent(self, query: str) -> str:
        """Handle update queries"""
        return """System Updates:
  Check updates: sudo apt update
  List upgrades: apt list --upgradable
  Install updates: sudo apt upgrade -y
  Full upgrade: sudo apt full-upgrade"""
    
    def _handle_security_intent(self, query: str) -> str:
        """Handle security queries"""
        return """Security Checks:
  Firewall: sudo ufw status
  Open ports: netstat -tulpn
  Failed logins: lastb | head -10
  Running services: systemctl list-units --type=service"""
