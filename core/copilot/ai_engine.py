"""AI Copilot Engine for Mimir"""
import os
import subprocess
import json
import psutil
from datetime import datetime
import platform

class AICopilot:
    """AI-powered Linux assistant"""
    
    def __init__(self):
        self.context = []
        self.command_history = []
        self.system_info = self._get_system_info()
        
    def _get_system_info(self):
        """Get comprehensive system info"""
        return {
            'os': platform.system(),
            'os_version': platform.version(),
            'hostname': platform.node(),
            'cpu': psutil.cpu_count(),
            'memory': psutil.virtual_memory().total / 1024**3,
            'python': platform.python_version()
        }
    
    def suggest_command(self, task_description):
        """Suggest a Linux command based on task description"""
        suggestions = {
            'find large files': 'find / -type f -size +100M 2>/dev/null | head -20',
            'check disk space': 'df -h',
            'check memory': 'free -h',
            'check processes': 'ps aux --sort=-%cpu | head -20',
            'kill process': 'kill -9 [PID]',
            'backup directory': 'tar -czf backup.tar.gz [directory]',
            'monitor network': 'iftop or nethogs',
            'check logs': 'journalctl -xe',
            'update system': 'sudo apt update && sudo apt upgrade -y',
            'clean system': 'sudo apt autoremove && sudo apt autoclean',
            'check temperature': 'sensors',
            'check users': 'who',
            'check services': 'systemctl list-units --type=service',
            'check ports': 'netstat -tulpn',
            'check firewall': 'sudo ufw status',
        }
        
        for key, command in suggestions.items():
            if key in task_description.lower():
                return {
                    'command': command,
                    'explanation': f"This command will {key}",
                    'confidence': 0.9
                }
        
        # Default suggestion
        return {
            'command': f"man -k {task_description}",
            'explanation': "Searching man pages for related commands",
            'confidence': 0.5
        }
    
    def explain_command(self, command):
        """Explain what a Linux command does"""
        explanations = {
            'ls': 'List directory contents',
            'cd': 'Change directory',
            'pwd': 'Print working directory',
            'cp': 'Copy files or directories',
            'mv': 'Move/rename files or directories',
            'rm': 'Remove files or directories',
            'mkdir': 'Create directories',
            'rmdir': 'Remove empty directories',
            'touch': 'Create empty files or update timestamps',
            'cat': 'Concatenate and display files',
            'grep': 'Search for patterns in files',
            'find': 'Search for files in directory hierarchy',
            'ps': 'Report process status',
            'kill': 'Terminate processes',
            'top': 'Display Linux processes',
            'htop': 'Interactive process viewer',
            'df': 'Report file system disk space usage',
            'du': 'Estimate file space usage',
            'free': 'Display memory usage',
            'uname': 'Print system information',
            'whoami': 'Print current user',
            'sudo': 'Execute command as superuser',
            'apt': 'Package management tool',
            'systemctl': 'Control systemd system and service manager',
            'journalctl': 'Query systemd journal',
            'ssh': 'OpenSSH remote login client',
            'scp': 'Secure copy (remote file copy)',
            'wget': 'Network downloader',
            'curl': 'Transfer data from or to a server',
        }
        
        cmd = command.split()[0]
        if cmd in explanations:
            return {
                'command': command,
                'explanation': explanations[cmd],
                'examples': self._get_examples(cmd)
            }
        else:
            return {
                'command': command,
                'explanation': f"Run 'man {cmd}' for detailed information",
                'examples': []
            }
    
    def _get_examples(self, cmd):
        """Get examples for common commands"""
        examples = {
            'ls': ['ls -la', 'ls *.txt', 'ls -lh'],
            'grep': ['grep "error" logfile.txt', 'grep -r "TODO" .', 'ps aux | grep python'],
            'find': ['find . -name "*.py"', 'find / -size +100M', 'find . -mtime -7'],
            'kill': ['kill -9 1234', 'killall firefox', 'pkill python'],
        }
        return examples.get(cmd, [])
    
    def diagnose_issue(self, issue_description):
        """Diagnose system issues"""
        issues = {
            'slow': self._diagnose_slow,
            'memory': self._diagnose_memory,
            'disk': self._diagnose_disk,
            'cpu': self._diagnose_cpu,
            'network': self._diagnose_network,
            'crash': self._diagnose_crash,
        }
        
        for key, diagnostic in issues.items():
            if key in issue_description.lower():
                return diagnostic()
        
        return self._general_diagnosis()
    
    def _diagnose_slow(self):
        """Diagnose slow system"""
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        issues = []
        if cpu > 80:
            issues.append(f"High CPU: {cpu}%")
        if mem.percent > 80:
            issues.append(f"High Memory: {mem.percent}%")
        if disk.percent > 85:
            issues.append(f"Low Disk: {disk.percent}%")
        
        suggestions = []
        if cpu > 80:
            suggestions.append("Run 'top' to find CPU hogs")
            suggestions.append("Consider: kill -9 [high CPU PID]")
        if mem.percent > 80:
            suggestions.append("Clear cache: sync && echo 3 | sudo tee /proc/sys/vm/drop_caches")
        if disk.percent > 85:
            suggestions.append("Clean packages: sudo apt clean")
            suggestions.append("Remove old logs: sudo journalctl --vacuum-time=3d")
        
        return {
            'issue': 'System Performance',
            'diagnosis': issues,
            'suggestions': suggestions,
            'severity': 'critical' if len(issues) > 1 else 'warning'
        }
    
    def _diagnose_memory(self):
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        issues = []
        if mem.percent > 90:
            issues.append(f"Critical memory: {mem.percent}%")
        elif mem.percent > 75:
            issues.append(f"High memory: {mem.percent}%")
        
        return {
            'issue': 'Memory Usage',
            'diagnosis': issues + [f"Swap: {swap.percent}%"],
            'suggestions': [
                "Check top memory processes: ps aux --sort=-%mem | head -10",
                "Clear cache: sync && echo 3 | sudo tee /proc/sys/vm/drop_caches",
                "Consider adding more RAM if persistent"
            ]
        }
    
    def _diagnose_disk(self):
        disk = psutil.disk_usage('/')
        
        issues = []
        if disk.percent > 95:
            issues.append(f"Critical disk space: {disk.percent}%")
        elif disk.percent > 85:
            issues.append(f"Low disk space: {disk.percent}%")
        
        return {
            'issue': 'Disk Usage',
            'diagnosis': issues + [f"Free: {disk.free/1024**3:.1f}GB"],
            'suggestions': [
                "Find large files: find / -type f -size +100M 2>/dev/null",
                "Clean packages: sudo apt clean",
                "Remove old kernels: sudo apt autoremove",
                "Clear journal: sudo journalctl --vacuum-time=7d"
            ]
        }
    
    def _diagnose_cpu(self):
        cpu = psutil.cpu_percent(interval=1, percpu=True)
        
        return {
            'issue': 'CPU Usage',
            'diagnosis': [f"Total: {sum(cpu)/len(cpu):.1f}%", f"Cores: {len(cpu)}"],
            'suggestions': [
                "Check top processes: top -b -n 1 | head -20",
                "Check temperature: sensors",
                "Consider process priorities: renice"
            ]
        }
    
    def _diagnose_network(self):
        net = psutil.net_io_counters()
        connections = psutil.net_connections()
        
        return {
            'issue': 'Network Status',
            'diagnosis': [
                f"Sent: {net.bytes_sent/1024**2:.1f}MB",
                f"Received: {net.bytes_recv/1024**2:.1f}MB",
                f"Connections: {len(connections)}"
            ],
            'suggestions': [
                "Check open ports: netstat -tulpn",
                "Monitor traffic: iftop or nethogs",
                "Test connectivity: ping -c 4 google.com"
            ]
        }
    
    def _diagnose_crash(self):
        try:
            with open('/var/log/syslog', 'r') as f:
                logs = f.readlines()[-50:]
                errors = [l for l in logs if 'error' in l.lower()]
        except:
            errors = []
        
        return {
            'issue': 'System Crash Analysis',
            'diagnosis': [f"Recent errors: {len(errors)}"],
            'suggestions': [
                "Check full logs: journalctl -xe",
                "Check kernel messages: dmesg | tail -20",
                "Check system status: systemctl --failed"
            ]
        }
    
    def _general_diagnosis(self):
        return {
            'issue': 'General System Check',
            'diagnosis': ['Running standard diagnostics'],
            'suggestions': [
                "Run 'mimir status' for overview",
                "Check 'mimir health' for health score",
                "Run 'mimir alerts' for active alerts"
            ]
        }
    
    def suggest_optimization(self):
        """Suggest system optimizations"""
        optimizations = []
        
        # Memory optimization
        mem = psutil.virtual_memory()
        if mem.percent > 80:
            optimizations.append({
                'area': 'memory',
                'suggestion': 'Clear memory cache',
                'command': 'sync && echo 3 | sudo tee /proc/sys/vm/drop_caches',
                'benefit': 'Free up RAM'
            })
        
        # Disk optimization
        disk = psutil.disk_usage('/')
        if disk.percent > 80:
            optimizations.append({
                'area': 'disk',
                'suggestion': 'Clean package cache',
                'command': 'sudo apt clean',
                'benefit': 'Free disk space'
            })
        
        # CPU optimization
        cpu = psutil.cpu_percent()
        if cpu > 70:
            processes = []
            for proc in psutil.process_iter(['name', 'cpu_percent']):
                if proc.info['cpu_percent'] > 20:
                    processes.append(proc.info)
            
            if processes:
                optimizations.append({
                    'area': 'cpu',
                    'suggestion': 'High CPU processes detected',
                    'processes': processes[:3],
                    'benefit': 'Reduce CPU load'
                })
        
        return optimizations

