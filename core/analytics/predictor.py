"""Predictive analytics for system issues"""
import psutil
import time
import numpy as np
from collections import deque
from datetime import datetime, timedelta

class SystemPredictor:
    """Predict future system issues based on historical data"""
    
    def __init__(self, history_size=100):
        self.cpu_history = deque(maxlen=history_size)
        self.memory_history = deque(maxlen=history_size)
        self.disk_history = deque(maxlen=history_size)
        self.timestamps = deque(maxlen=history_size)
    
    def record_current(self):
        """Record current system metrics"""
        self.cpu_history.append(psutil.cpu_percent())
        self.memory_history.append(psutil.virtual_memory().percent)
        self.disk_history.append(psutil.disk_usage('/').percent)
        self.timestamps.append(time.time())
    
    def predict_cpu(self, minutes_ahead=60):
        """Predict CPU usage in X minutes"""
        if len(self.cpu_history) < 10:
            return None
        
        # Simple linear regression on last 20 points
        recent = list(self.cpu_history)[-20:]
        if len(recent) < 5:
            return None
        
        x = np.arange(len(recent))
        y = np.array(recent)
        slope, intercept = np.polyfit(x, y, 1)
        
        # Predict future value
        future_x = len(recent) + (minutes_ahead / 5)  # Assuming 5s intervals
        prediction = slope * future_x + intercept
        
        return max(0, min(100, prediction))
    
    def predict_memory(self, minutes_ahead=60):
        """Predict memory usage in X minutes"""
        if len(self.memory_history) < 10:
            return None
        
        recent = list(self.memory_history)[-20:]
        x = np.arange(len(recent))
        y = np.array(recent)
        slope, intercept = np.polyfit(x, y, 1)
        
        future_x = len(recent) + (minutes_ahead / 5)
        prediction = slope * future_x + intercept
        
        return max(0, min(100, prediction))
    
    def predict_disk_full(self):
        """Predict when disk will be full (days)"""
        if len(self.disk_history) < 10:
            return None
        
        recent = list(self.disk_history)[-20:]
        x = np.arange(len(recent))
        y = np.array(recent)
        slope, intercept = np.polyfit(x, y, 1)
        
        if slope <= 0:
            return None  # Not filling up
        
        # Calculate days until 95% full
        days_to_full = (95 - y[-1]) / (slope * 24 * 60 / 5)  # Convert slope to % per day
        return max(0, days_to_full)
    
    def get_predictions(self):
        """Get all predictions"""
        self.record_current()
        
        return {
            'cpu': {
                'current': self.cpu_history[-1] if self.cpu_history else 0,
                'predicted_1h': self.predict_cpu(60),
                'trend': 'increasing' if len(self.cpu_history) > 5 and self.cpu_history[-1] > self.cpu_history[-5] else 'stable'
            },
            'memory': {
                'current': self.memory_history[-1] if self.memory_history else 0,
                'predicted_1h': self.predict_memory(60),
                'trend': 'increasing' if len(self.memory_history) > 5 and self.memory_history[-1] > self.memory_history[-5] else 'stable'
            },
            'disk': {
                'current': self.disk_history[-1] if self.disk_history else 0,
                'days_to_full': self.predict_disk_full(),
                'trend': 'increasing' if len(self.disk_history) > 5 and self.disk_history[-1] > self.disk_history[-5] else 'stable'
            }
        }
