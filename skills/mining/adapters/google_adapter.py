"""Google Gemini API adapter."""

import os
import logging
from typing import Dict, Any
from .base import BaseAdapter

logger = logging.getLogger("GoogleAdapter")

# Pricing per 1M tokens (input, output) - approximate
PRICING = {
    "gemini-2.0-flash": (0.0, 0.0),  # Free tier
    "gemini-1.5-pro": (1.25, 5.00),
    "gemini-1.5-flash": (0.075, 0.30),
    "gemini-1.0-pro": (1.25, 5.00),
}

class GoogleAdapter(BaseAdapter):
    """Adapter for Google Gemini API."""
    
    def __init__(self, api_key: str, timeout: int = 30, max_retries: int = 3):
        super().__init__(api_key, timeout, max_retries)
        self.base_url = os.getenv("GOOGLE_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
    
    def execute(self, prompt: str, model: str = "gemini-2.0-flash", **kwargs) -> Dict[str, Any]:
        """Execute Google Gemini API call."""
        try:
            import requests
            
            url = f"{self.base_url}/models/{model}:generateContent"
            params = {"key": self.api_key}
            
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "maxOutputTokens": kwargs.get("max_tokens", 1000),
                    "temperature": kwargs.get("temperature", 0.7),
                }
            }
            
            response = requests.post(
                url, params=params, json=payload, timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract response
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            
            # Estimate tokens (rough)
            tokens = len(text.split()) * 1.3
            pricing = PRICING.get(model, (0.075, 0.30))
            cost = (tokens / 1_000_000 * pricing[0])
            
            return {
                "response": text,
                "tokens": int(tokens),
                "cost": cost,
                "model": model
            }
            
        except Exception as e:
            return self._handle_error(e)
    
    def validate_key(self) -> bool:
        """Validate Google API key."""
        try:
            import requests
            url = f"{self.base_url}/models?key={self.api_key}"
            response = requests.get(url, timeout=10)
            return response.status_code == 200
        except Exception:
            return False
