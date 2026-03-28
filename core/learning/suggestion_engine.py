"""Context-aware command suggestion engine for Mimir"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from collections import Counter
import re

class SuggestionEngine:
    """Learns from user commands and suggests intelligent completions"""
    
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = Path.home() / ".mimir" / "data" / "learning.db"
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self.context = {}
    
    def _init_db(self):
        """Initialize learning database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Command history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS command_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command TEXT NOT NULL,
                context TEXT,
                success BOOLEAN DEFAULT 1,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                frequency INTEGER DEFAULT 1
            )
        ''')
        
        # Command patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS command_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern TEXT NOT NULL,
                suggestion TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                uses INTEGER DEFAULT 0
            )
        ''')
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def record_command(self, command, success=True, context=None):
        """Record a command and its success/failure"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if command exists
        cursor.execute(
            "SELECT id, frequency FROM command_history WHERE command = ?",
            (command,)
        )
        result = cursor.fetchone()
        
        if result:
            # Update frequency
            cursor.execute(
                "UPDATE command_history SET frequency = frequency + 1, timestamp = CURRENT_TIMESTAMP WHERE id = ?",
                (result[0],)
            )
        else:
            # Insert new command
            cursor.execute(
                "INSERT INTO command_history (command, context, success) VALUES (?, ?, ?)",
                (command, json.dumps(context or {}), success)
            )
        
        conn.commit()
        conn.close()
    
    def suggest_completions(self, partial, context=None, limit=5):
        """Suggest command completions based on partial input"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Search command history
        cursor.execute('''
            SELECT command, frequency 
            FROM command_history 
            WHERE command LIKE ? 
            ORDER BY frequency DESC, timestamp DESC 
            LIMIT ?
        ''', (f"{partial}%", limit * 2))
        
        suggestions = []
        for cmd, freq in cursor.fetchall():
            suggestions.append({
                'command': cmd,
                'confidence': min(0.9, freq / 100),
                'source': 'history'
            })
        
        # Check patterns
        cursor.execute('''
            SELECT pattern, suggestion, confidence 
            FROM command_patterns 
            WHERE ? LIKE pattern OR pattern LIKE ?
            ORDER BY confidence DESC, uses DESC
            LIMIT ?
        ''', (partial, f"%{partial}%", limit - len(suggestions)))
        
        for pattern, suggestion, confidence in cursor.fetchall():
            suggestions.append({
                'command': suggestion,
                'confidence': confidence,
                'source': 'pattern'
            })
        
        conn.close()
        
        # Remove duplicates and sort by confidence
        seen = set()
        unique = []
        for s in suggestions:
            if s['command'] not in seen:
                seen.add(s['command'])
                unique.append(s)
        
        return sorted(unique, key=lambda x: x['confidence'], reverse=True)[:limit]
    
    def learn_pattern(self, pattern, suggestion, confidence=0.5):
        """Teach Mimir a new command pattern"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO command_patterns (pattern, suggestion, confidence, uses)
            VALUES (?, ?, ?, COALESCE((SELECT uses FROM command_patterns WHERE pattern = ?), 0) + 1)
        ''', (pattern, suggestion, confidence, pattern))
        
        conn.commit()
        conn.close()
    
    def get_frequent_commands(self, limit=10):
        """Get most frequently used commands"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT command, frequency 
            FROM command_history 
            ORDER BY frequency DESC 
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_command_chain(self, command):
        """Suggest next commands based on what follows this command"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get next commands
        cursor.execute('''
            SELECT c2.command, COUNT(*) as count
            FROM command_history c1
            JOIN command_history c2 ON c1.id + 1 = c2.id
            WHERE c1.command = ? AND c2.id > c1.id
            GROUP BY c2.command
            ORDER BY count DESC
            LIMIT 5
        ''', (command,))
        
        results = cursor.fetchall()
        conn.close()
        return [{'command': cmd, 'probability': count / 100} for cmd, count in results]
