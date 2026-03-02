"""OpenAI API adapter."""

import os
import logging
from typing import Dict, Any
from .base import BaseAdapter

logger = logging.getLogger("OpenAIAdapter")

# Pricing per 1M tokens (input, output)
PRICING = {
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4-turbo": (10.00, 30.00),
    "gpt-4": (30.00, 60.00),
    "gpt-3.5-turbo": (0.50, 1.50),
}

class OpenAIAdapter(BaseAdapter):
    """Adapter for OpenAI API."""
    
    def __init__(self, api_key: str, timeout: int = 30, max_retries: int = 3):
        super().__init__(api_key, timeout, max_retries)
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    def execute(self, prompt: str, model: str = "gpt-4o", **kwargs) -> Dict[str, Any]:
        """Execute OpenAI API call."""
        try:
            import requests
            
            url = f"{self.base_url}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": kwargs.get("max_tokens", 1000),
                "temperature": kwargs.get("temperature", 0.7),
            }
            
            response = requests.post(
                url, headers=headers, json=payload, timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            # Calculate cost
            input_tokens = data.get("usage", {}).get("prompt_tokens", 0)
            output_tokens = data.get("usage", {}).get("completion_tokens", 0)
            pricing = PRICING.get(model, (2.50, 10.00))
            cost = (input_tokens / 1_000_000 * pricing[0]) + (output_tokens / 1_000_000 * pricing[1])
            
            return {
                "response": data["choices"][0]["message"]["content"],
                "tokens": input_tokens + output_tokens,
                "cost": cost,
                "model": model
            }
            
        except Exception as e:
            return self._handle_error(e)
    
    def validate_key(self) -> bool:
        """Validate OpenAI API key."""
        try:
            import requests
            url = f"{self.base_url}/models"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(url, headers=headers, timeout=10)
            return response.status_code == 200
        except Exception:
            return False
