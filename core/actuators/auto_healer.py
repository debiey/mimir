"""Auto-healing system for Mimir"""
import os
import subprocess
import psutil
from datetime import datetime

class AutoHealer:
    """Automatically fixes common system issues"""
    
    def __init__(self, config=None):
        self.config = config
        self.healing_history = []
        self.dry_run = False
        self.safety_mode = True
    
    def heal(self, issue_type=None, auto_confirm=False):
        fixes = []
        
        if issue_type == 'memory' or not issue_type:
            fixes.extend(self._fix_memory())
        
        if issue_type == 'disk' or not issue_type:
            fixes.extend(self._fix_disk())
        
        if issue_type == 'process' or not issue_type:
            fixes.extend(self._fix_processes())
        
        if issue_type == 'system' or not issue_type:
            fixes.extend(self._fix_system())
        
        for fix in fixes:
            self.healing_history.append({
                'timestamp': datetime.now().isoformat(),
                'action': fix['action'],
                'result': fix['result'],
                'success': fix['success']
            })
        
        return fixes
    
    def _fix_memory(self):
        fixes = []
        memory = psutil.virtual_memory()
        
        if memory.percent > 90:
            fixes.append(self._run_command(
                "Clear memory cache",
                "sync && echo 3 | sudo tee /proc/sys/vm/drop_caches",
                "Freed up memory by clearing cache",
                "Could not clear cache (need sudo?)"
            ))
        
        return fixes
    
    def _fix_disk(self):
        fixes = []
        disk = psutil.disk_usage('/')
        
        if disk.percent > 85:
            fixes.append(self._run_command(
                "Clean package cache",
                "sudo apt clean",
                "Cleaned package cache",
                "Could not clean package cache"
            ))
            
            fixes.append(self._run_command(
                "Clean journal logs",
                "sudo journalctl --vacuum-time=3d",
                "Removed old journal logs",
                "Could not clean journal logs"
            ))
        
        return fixes
    
    def _fix_processes(self):
        fixes = []
        zombies = self._find_zombies()
        for zombie in zombies:
            fixes.append(self._run_command(
                f"Kill zombie process {zombie['pid']}",
                f"sudo kill -9 {zombie['pid']}",
                f"Killed zombie process {zombie['name']}",
                f"Could not kill zombie process {zombie['pid']}"
            ))
        return fixes
    
    def _fix_system(self):
        fixes = []
        try:
            result = subprocess.run(
                ['apt', 'list', '--upgradable'],
                capture_output=True, text=True
            )
            updates = len([l for l in result.stdout.split('\n') if '/' in l])
            
            if updates > 10:
                fixes.append({
                    'action': "System updates available",
                    'result': f"{updates} updates available. Run 'sudo apt upgrade' manually.",
                    'success': True,
                    'command': None
                })
        except:
            pass
        return fixes
    
    def _run_command(self, action, command, success_msg, error_msg):
        if self.dry_run:
            return {
                'action': action,
                'result': f"[DRY RUN] Would run: {command}",
                'success': True,
                'command': command
            }
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return {
                    'action': action,
                    'result': success_msg,
                    'success': True,
                    'command': command
                }
            else:
                return {
                    'action': action,
                    'result': f"{error_msg}: {result.stderr[:100]}",
                    'success': False,
                    'command': command
                }
        except Exception as e:
            return {
                'action': action,
                'result': f"{error_msg}: {str(e)}",
                'success': False,
                'command': command
            }
    
    def _find_zombies(self):
        zombies = []
        for proc in psutil.process_iter(['pid', 'name', 'status']):
            try:
                if proc.info['status'] == 'zombie':
                    zombies.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name']
                    })
            except:
                pass
        return zombies
