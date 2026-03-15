"""System health scoring module"""
import psutil
import time
import os
from datetime import datetime

class HealthScore:
    """Calculates overall system health score"""
    
    def __init__(self):
        self.score = 100
        self.breakdown = {}
        self.history = []
        self.last_check = None
    
    def calculate(self):
        self.score = 100
        self.breakdown = {}
        
        cpu = psutil.cpu_percent(interval=1)
        cpu_score = max(0, 30 - (cpu * 0.3))
        self.score += cpu_score - 30
        self.breakdown['cpu'] = {
            'score': cpu_score,
            'value': cpu,
            'max': 30,
            'status': self._get_status(cpu, 70, 90)
        }
        
        memory = psutil.virtual_memory().percent
        mem_score = max(0, 25 - (memory * 0.25))
        self.score += mem_score - 25
        self.breakdown['memory'] = {
            'score': mem_score,
            'value': memory,
            'max': 25,
            'status': self._get_status(memory, 75, 90)
        }
        
        disk = psutil.disk_usage('/').percent
        disk_score = max(0, 20 - (disk * 0.2))
        self.score += disk_score - 20
        self.breakdown['disk'] = {
            'score': disk_score,
            'value': disk,
            'max': 20,
            'status': self._get_status(disk, 75, 90)
        }
        
        load = os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0
        cpu_count = psutil.cpu_count()
        load_per_cpu = load / cpu_count if cpu_count else 0
        load_score = max(0, 15 - (load_per_cpu * 5))
        self.score += load_score - 15
        self.breakdown['load'] = {
            'score': load_score,
            'value': load,
            'max': 15,
            'status': self._get_status(load_per_cpu * 100, 50, 80)
        }
        
        uptime_seconds = time.time() - psutil.boot_time()
        uptime_days = uptime_seconds / 86400
        uptime_score = max(0, 10 - uptime_days * 0.5)
        self.score += uptime_score - 10
        self.breakdown['uptime'] = {
            'score': uptime_score,
            'value': uptime_days,
            'max': 10,
            'status': 'good' if uptime_days < 7 else 'warning' if uptime_days < 14 else 'critical'
        }
        
        self.score = max(0, min(100, self.score))
        self.last_check = datetime.now()
        
        self.history.append({
            'timestamp': self.last_check.isoformat(),
            'score': self.score,
            'breakdown': self.breakdown
        })
        
        if len(self.history) > 100:
            self.history = self.history[-100:]
        
        return self.score
    
    def _get_status(self, value, warning_threshold, critical_threshold):
        if value >= critical_threshold:
            return 'critical'
        elif value >= warning_threshold:
            return 'warning'
        else:
            return 'good'
    
    def get_score(self):
        return self.calculate()
    
    def get_details(self):
        return {
            'score': self.score,
            'breakdown': self.breakdown,
            'timestamp': self.last_check.isoformat() if self.last_check else None
        }
    
    def get_emoji(self):
        if self.score >= 90:
            return "🌟"
        elif self.score >= 75:
            return "👍"
        elif self.score >= 60:
            return "⚠️"
        elif self.score >= 40:
            return "🔴"
        else:
            return "💀"

