"""Base adapter interface for LLM providers."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger("AdapterBase")

class BaseAdapter(ABC):
    """Abstract base class for LLM API adapters."""
    
    def __init__(self, api_key: str, timeout: int = 30, max_retries: int = 3):
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
    
    @abstractmethod
    def execute(self, prompt: str, model: str, **kwargs) -> Dict[str, Any]:
        """
        Execute LLM inference.
        
        Args:
            prompt: The input prompt
            model: Model identifier (e.g., 'gpt-4', 'claude-3-opus')
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Dict with keys: 'response' (str), 'tokens' (int), 'cost' (float)
        """
        pass
    
    @abstractmethod
    def validate_key(self) -> bool:
        """Check if API key is valid."""
        pass
    
    def _handle_error(self, error: Exception) -> Dict[str, Any]:
        """Standardized error handling."""
        logger.error(f"Adapter error: {error}")
        return {
            "error": str(error),
            "response": None,
            "tokens": 0,
            "cost": 0.0
        }
