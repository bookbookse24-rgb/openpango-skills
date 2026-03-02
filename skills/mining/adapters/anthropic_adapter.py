"""Anthropic API adapter."""

import os
import logging
from typing import Dict, Any
from .base import BaseAdapter

logger = logging.getLogger("AnthropicAdapter")

# Pricing per 1M tokens (input, output)
PRICING = {
    "claude-opus-4-5": (15.00, 75.00),
    "claude-sonnet-4-6": (3.00, 15.00),
    "claude-haiku-4-5": (0.80, 4.00),
    "claude-3-opus": (15.00, 75.00),
    "claude-3-sonnet": (3.00, 15.00),
    "claude-3-haiku": (0.25, 1.25),
}

class AnthropicAdapter(BaseAdapter):
    """Adapter for Anthropic Claude API."""
    
    def __init__(self, api_key: str, timeout: int = 30, max_retries: int = 3):
        super().__init__(api_key, timeout, max_retries)
        self.base_url = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com/v1")
    
    def execute(self, prompt: str, model: str = "claude-sonnet-4-6", **kwargs) -> Dict[str, Any]:
        """Execute Anthropic API call."""
        try:
            import requests
            
            url = f"{self.base_url}/messages"
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "max_tokens": kwargs.get("max_tokens", 1000),
                "messages": [{"role": "user", "content": prompt}],
            }
            
            if "temperature" in kwargs:
                payload["temperature"] = kwargs["temperature"]
            
            response = requests.post(
                url, headers=headers, json=payload, timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            # Calculate cost
            input_tokens = data.get("usage", {}).get("input_tokens", 0)
            output_tokens = data.get("usage", {}).get("output_tokens", 0)
            pricing = PRICING.get(model, (3.00, 15.00))
            cost = (input_tokens / 1_000_000 * pricing[0]) + (output_tokens / 1_000_000 * pricing[1])
            
            return {
                "response": data["content"][0]["text"],
                "tokens": input_tokens + output_tokens,
                "cost": cost,
                "model": model
            }
            
        except Exception as e:
            return self._handle_error(e)
    
    def validate_key(self) -> bool:
        """Validate Anthropic API key."""
        try:
            import requests
            url = f"{self.base_url}/messages"
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            payload = {"model": "claude-haiku-4-5", "max_tokens": 1, "messages": [{"role": "user", "content": "hi"}]}
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            return response.status_code in (200, 201)
        except Exception:
            return False
