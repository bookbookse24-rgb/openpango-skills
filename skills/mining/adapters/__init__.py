"""LLM Provider Adapters.

Unified interface for multiple LLM providers with standardized
execute() and validate_key() methods.
"""

from .base import BaseAdapter
from .openai_adapter import OpenAIAdapter
from .anthropic_adapter import AnthropicAdapter
from .google_adapter import GoogleAdapter
from .ollama_adapter import OllamaAdapter

__all__ = [
    "BaseAdapter",
    "OpenAIAdapter", 
    "AnthropicAdapter",
    "GoogleAdapter",
    "OllamaAdapter",
]

# Provider mapping for factory
ADAPTERS = {
    "openai": OpenAIAdapter,
    "anthropic": AnthropicAdapter,
    "google": GoogleAdapter,
    "ollama": OllamaAdapter,
}

def get_adapter(provider: str, api_key: str = "", **kwargs):
    """Factory function to get adapter by provider name."""
    adapter_class = ADAPTERS.get(provider.lower())
    if not adapter_class:
        raise ValueError(f"Unknown provider: {provider}")
    return adapter_class(api_key, **kwargs)
