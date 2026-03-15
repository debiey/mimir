"""Alert management system for Mimir"""
import os
import json
import psutil
from datetime import datetime
from pathlib import Path

class AlertManager:
    """Manages system alerts and notifications"""
    
    def __init__(self, config=None):
        self.config = config
        self.alerts = []
        self.alert_history = []
        self.history_file = Path.home() / ".mimir" / "data" / "alert_history.json"
        self.load_history()
        
        self.thresholds = {
            'cpu': {'warning': 70, 'critical': 90},
            'memory': {'warning': 80, 'critical': 95},
            'disk': {'warning': 80, 'critical': 95},
            'temperature': {'warning': 75, 'critical': 85},
            'load': {'warning': 5, 'critical': 10},
            'process_count': {'warning': 500, 'critical': 1000}
        }
    
    def load_history(self):
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    self.alert_history = json.load(f)
            except:
                self.alert_history = []
    
    def save_history(self):
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.history_file, 'w') as f:
            json.dump(self.alert_history[-100:], f, indent=2)
    
    def check_all(self):
        self.alerts = []
        
        cpu = psutil.cpu_percent(interval=1)
        self._check_threshold('cpu', cpu, f"CPU usage at {cpu}%")
        
        memory = psutil.virtual_memory()
        self._check_threshold('memory', memory.percent, f"Memory usage at {memory.percent}%")
        
        disk = psutil.disk_usage('/')
        self._check_threshold('disk', disk.percent, f"Disk usage at {disk.percent}%")
        
        load = os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0
        self._check_threshold('load', load, f"System load at {load:.2f}")
        
        process_count = len(psutil.pids())
        self._check_threshold('process_count', process_count, f"Process count: {process_count}")
        
        self._check_temperature()
        return self.alerts
    
    def _check_threshold(self, metric, value, message):
        if metric in self.thresholds:
            if value > self.thresholds[metric]['critical']:
                alert = Alert('critical', metric, message, value)
                self.alerts.append(alert)
                self.alert_history.append(alert.to_dict())
            elif value > self.thresholds[metric]['warning']:
                alert = Alert('warning', metric, message, value)
                self.alerts.append(alert)
                self.alert_history.append(alert.to_dict())
    
    def _check_temperature(self):
        try:
            if os.path.exists('/sys/class/thermal/thermal_zone0/temp'):
                with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                    temp = int(f.read().strip()) / 1000
                    self._check_threshold('temperature', temp, f"CPU temperature at {temp:.1f}°C")
        except:
            pass
    
    def send_notifications(self):
        for alert in self.alerts:
            if alert.severity == 'critical':
                self._send_desktop_notification(alert)
    
    def _send_desktop_notification(self, alert):
        try:
            title = f"🚨 Mimir Alert: {alert.metric.upper()}"
            os.system(f'notify-send -u critical "{title}" "{alert.message}"')
        except:
            pass
    
    def get_active_alerts(self):
        return self.alerts
    
    def get_alert_history(self, limit=10):
        return self.alert_history[-limit:]

class Alert:
    def __init__(self, severity, metric, message, value=None):
        self.severity = severity
        self.metric = metric
        self.message = message
        self.value = value
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            'severity': self.severity,
            'metric': self.metric,
            'message': self.message,
            'value': self.value,
            'timestamp': self.timestamp
        }
    
    def __str__(self):
        emoji = "🔴" if self.severity == 'critical' else "🟡"
        return f"{emoji} [{self.severity.upper()}] {self.message}"
