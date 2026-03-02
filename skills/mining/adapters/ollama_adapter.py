"""Ollama local inference adapter."""

import os
import logging
from typing import Dict, Any
from .base import BaseAdapter

logger = logging.getLogger("OllamaAdapter")

# Ollama is self-hosted, cost is hardware-dependent (assume $0)
PRICING = {
    "llama3": (0.0, 0.0),
    "llama3.1": (0.0, 0.0),
    "mistral": (0.0, 0.0),
    "codellama": (0.0, 0.0),
    "phi3": (0.0, 0.0),
    "gemma": (0.0, 0.0),
}

class OllamaAdapter(BaseAdapter):
    """Adapter for local Ollama inference."""
    
    def __init__(self, api_key: str = "", base_url: str = None, timeout: int = 60, max_retries: int = 3):
        # api_key unused for local Ollama
        super().__init__(api_key or "dummy", timeout, max_retries)
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    def execute(self, prompt: str, model: str = "llama3", **kwargs) -> Dict[str, Any]:
        """Execute Ollama local inference."""
        try:
            import requests
            
            url = f"{self.base_url}/api/generate"
            
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "num_predict": kwargs.get("max_tokens", 1000),
                }
            }
            
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            text = data.get("response", "")
            tokens = data.get("eval_count", len(text.split()))
            
            return {
                "response": text,
                "tokens": tokens,
                "cost": 0.0,  # Self-hosted, hardware cost varies
                "model": model
            }
            
        except Exception as e:
            return self._handle_error(e)
    
    def validate_key(self) -> bool:
        """Check if Ollama is running."""
        try:
            import requests
            url = f"{self.base_url}/api/tags"
            response = requests.get(url, timeout=10)
            return response.status_code == 200
        except Exception:
            return False
