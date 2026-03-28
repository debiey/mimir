"""Ollama client for local LLM integration"""
import requests
import json
from typing import Optional, List, Dict, Any

class OllamaClient:
    """Client for interacting with local Ollama instance"""
    
    def __init__(self, model: str = "mistral", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.context = []
        self._check_connection()
    
    def _check_connection(self):
        """Check if Ollama is running and model available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                available = [m['name'] for m in models]
                # Check if model exists (exact match or with :latest)
                model_match = None
                for avail in available:
                    if avail == self.model or avail == f"{self.model}:latest":
                        model_match = avail
                        break
                    if self.model in avail:
                        model_match = avail
                        break
                
                if model_match:
                    self.model = model_match
                    print(f"✅ Ollama connected. Using model: {self.model}")
                else:
                    print(f"⚠️ Model '{self.model}' not found. Available: {available}")
            else:
                print("⚠️ Ollama running but unexpected response")
        except requests.exceptions.ConnectionError:
            print("❌ Ollama not running. Start with: ollama serve")
            print("   Then pull a model: ollama pull mistral")
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate a response from the model"""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            response = requests.post(url, json=payload, timeout=300)
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                return f"Error: {response.status_code} - {response.text}"
        except requests.exceptions.Timeout:
            return "Error: Request timed out. Model may be slow."
        except Exception as e:
            return f"Error: {e}"
    
    def chat(self, message: str, system_prompt: Optional[str] = None) -> str:
        """Chat mode with context retention"""
        self.context.append({"role": "user", "content": message})
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": self.context,
            "stream": False
        }
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            response = requests.post(url, json=payload, timeout=120)
            if response.status_code == 200:
                result = response.json()
                reply = result.get("message", {}).get("content", "")
                self.context.append({"role": "assistant", "content": reply})
                return reply.strip()
            else:
                return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error: {e}"
    
    def reset_context(self):
        """Clear conversation history"""
        self.context = []
    
    def list_models(self) -> List[str]:
        """List available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                return [m['name'] for m in response.json().get('models', [])]
            return []
        except:
            return []
    
    def test_connection(self) -> bool:
        """Test if Ollama is responding"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def generate_stream(self, prompt: str, system_prompt: Optional[str] = None):
        """Generate a response with streaming (for real-time feedback)"""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True
        }
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            response = requests.post(url, json=payload, stream=True, timeout=120)
            for line in response.iter_lines():
                if line:
                    yield json.loads(line).get("response", "")
        except Exception as e:
            yield f"Error: {e}"
