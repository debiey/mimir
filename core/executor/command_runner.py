"""Command execution with AI analysis"""
import subprocess
import shlex
import time
from datetime import datetime
from pathlib import Path

class CommandRunner:
    """Execute commands with AI-powered analysis"""
    
    def __init__(self, copilot=None):
        self.copilot = copilot
        self.history = []
        self.last_command = None
        self.last_result = None
    
    def run(self, command, ask_confirmation=True):
        """Execute a command with optional AI analysis"""
        # Parse command for safety
        cmd_parts = shlex.split(command)
        if not cmd_parts:
            return None
        
        # Check for dangerous commands
        dangerous = self._is_dangerous(command)
        if dangerous and ask_confirmation:
            print(f"\n⚠️ DANGEROUS COMMAND DETECTED: {command}")
            print(f"   Reason: {dangerous}")
            confirm = input("   Are you ABSOLUTELY sure? (yes/NO): ")
            if confirm.lower() != 'yes':
                print("   ❌ Command cancelled")
                return None
        
        # Ask for confirmation if requested
        if ask_confirmation and not dangerous:
            print(f"\n💡 About to run: {command}")
            confirm = input("   Run this command? (Y/n): ")
            if confirm.lower() == 'n':
                print("   ❌ Command cancelled")
                return None
        
        # Execute command
        print(f"\n🚀 Executing: {command}")
        start_time = time.time()
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            elapsed = time.time() - start_time
            
            # Store in history
            entry = {
                'command': command,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'elapsed': elapsed,
                'timestamp': datetime.now().isoformat()
            }
            self.history.append(entry)
            self.last_command = command
            self.last_result = entry
            
            # Display output
            if result.stdout:
                print(f"\n📤 OUTPUT:")
                print(result.stdout[:2000])  # Limit output
                if len(result.stdout) > 2000:
                    print(f"... (truncated, {len(result.stdout)} total chars)")
            
            if result.stderr:
                print(f"\n⚠️ ERRORS:")
                print(result.stderr[:1000])
            
            # Check if command failed
            if result.returncode != 0:
                print(f"\n❌ Command failed with exit code: {result.returncode}")
                self._analyze_failure(command, result)
            else:
                print(f"\n✅ Command succeeded in {elapsed:.2f}s")
            
            return entry
            
        except subprocess.TimeoutExpired:
            print(f"\n❌ Command timed out after 30 seconds")
            return None
        except Exception as e:
            print(f"\n❌ Error executing command: {e}")
            return None
    
    def _is_dangerous(self, command):
        """Check if command is dangerous"""
        dangerous_patterns = [
            ('rm -rf /', 'Potential system deletion'),
            ('dd if=', 'Low-level disk operation'),
            ('mkfs', 'Filesystem creation'),
            ('format', 'Disk formatting'),
            ('chmod 777', 'Overly permissive permissions'),
            ('> /dev/sd', 'Direct disk write'),
            ('sudo rm', 'Sudo deletion (use with caution)'),
        ]
        
        for pattern, reason in dangerous_patterns:
            if pattern in command:
                return reason
        return None
    
    def _analyze_failure_with_ai(self, command, result):
        """Use AI to analyze command failure"""
        if not self.copilot or not self.copilot.use_llm:
            print("\n💡 Tip: Enable 'llm on' for AI-powered error analysis")
            return
        
        print("\n🔍 AI Analyzing error...")
        
        prompt = f"""A user ran this command: {command}
        
It failed with exit code {result.returncode}.
Error output:
{result.stderr[:1000]}

Please provide:
1. What went wrong (in simple terms)
2. How to fix it (specific commands)
3. The correct command to achieve what they wanted (if applicable)"""

        try:
            analysis = self.copilot.llm.generate(prompt)
            print(f"\n🤖 AI ANALYSIS:\n{analysis}")
        except Exception as e:
            print(f"AI analysis failed: {e}")

# Update command_runner.py to use AI analysis
    def _analyze_failure(self, command, result):
        """Use AI to analyze command failure"""
        if self.copilot and self.copilot.use_llm:
            print("\n🔍 AI Analyzing error...")
            analysis = self.copilot.analyze_error(command, result.stderr, result.returncode)
            if analysis:
                print(f"\n🤖 AI ANALYSIS:\n{analysis}")
        else:
            print("\n💡 Enable 'llm on' for AI-powered error analysis")
            print("   Suggestions:")
            if "permission denied" in result.stderr.lower():
                print("   • Try with sudo: sudo " + command)
            if "not found" in result.stderr.lower():
                print("   • Install missing package: apt search [name]")
            if "command not found" in result.stderr.lower():
                print("   • Check spelling or install the package")
    
    def get_history(self, limit=10):
        """Get command history"""
        return self.history[-limit:]
    
    def suggest_fix(self, error_message):
        """Suggest fix for an error"""
        if not self.copilot or not self.copilot.use_llm:
            return None
        
        prompt = f"""This error occurred: {error_message}
        
Suggest a fix for this Linux error. Return only the command to fix it, no explanation."""

        try:
            return self.copilot.llm.generate(prompt)
        except:
            return None

# Example usage
if __name__ == "__main__":
    runner = CommandRunner()
    runner.run("ls -la")

