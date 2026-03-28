"""Optional cloud sync for Mimir (privacy-first)"""
import json
import hashlib
from pathlib import Path
from datetime import datetime
import requests
from cryptography.fernet import Fernet

class SyncManager:
    """Manages optional encrypted cloud sync"""
    
    def __init__(self, sync_dir=None, encrypt=True):
        if sync_dir is None:
            sync_dir = Path.home() / ".mimir" / "sync"
        self.sync_dir = sync_dir
        self.sync_dir.mkdir(parents=True, exist_ok=True)
        self.encrypt = encrypt
        self.key = None
        
        if encrypt:
            self._load_or_create_key()
    
    def _load_or_create_key(self):
        """Load or create encryption key"""
        key_file = self.sync_dir / "key.key"
        if key_file.exists():
            with open(key_file, 'rb') as f:
                self.key = f.read()
        else:
            self.key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(self.key)
    
    def encrypt_data(self, data):
        """Encrypt data before sync"""
        if not self.encrypt:
            return data
        f = Fernet(self.key)
        return f.encrypt(json.dumps(data).encode()).decode()
    
    def decrypt_data(self, encrypted):
        """Decrypt synced data"""
        if not self.encrypt:
            return encrypted
        f = Fernet(self.key)
        return json.loads(f.decrypt(encrypted.encode()).decode())
    
    def sync_to_server(self, data, server_url):
        """Sync data to remote server (user configurable)"""
        encrypted = self.encrypt_data(data)
        try:
            response = requests.post(f"{server_url}/sync", json={'data': encrypted})
            return response.status_code == 200
        except:
            return False
    
    def sync_from_server(self, server_url):
        """Sync data from remote server"""
        try:
            response = requests.get(f"{server_url}/sync")
            if response.status_code == 200:
                return self.decrypt_data(response.json()['data'])
        except:
            pass
        return None
