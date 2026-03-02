"""Unit tests for LLM adapters (mock mode)."""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adapters import get_adapter, OpenAIAdapter, AnthropicAdapter, GoogleAdapter, OllamaAdapter


class TestOpenAIAdapter(unittest.TestCase):
    """Test OpenAI adapter."""
    
    @patch('adapters.openai_adapter.requests.post')
    def test_execute(self, mock_post):
        """Test successful API call."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Hello"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5}
        }
        mock_post.return_value = mock_response
        
        adapter = OpenAIAdapter("test-key")
        result = adapter.execute("Hi", "gpt-4o")
        
        self.assertEqual(result["response"], "Hello")
        self.assertEqual(result["tokens"], 15)
        self.assertGreater(result["cost"], 0)
    
    def test_validate_key(self):
        """Test key validation."""
        adapter = OpenAIAdapter("invalid-key")
        # Will fail network call, returns False
        self.assertFalse(adapter.validate_key())


class TestAnthropicAdapter(unittest.TestCase):
    """Test Anthropic adapter."""
    
    @patch('adapters.anthropic_adapter.requests.post')
    def test_execute(self, mock_post):
        """Test successful API call."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "content": [{"text": "Hi there"}],
            "usage": {"input_tokens": 10, "output_tokens": 8}
        }
        mock_post.return_value = mock_response
        
        adapter = AnthropicAdapter("test-key")
        result = adapter.execute("Hello", "claude-haiku-4-5")
        
        self.assertEqual(result["response"], "Hi there")
        self.assertIn("cost", result)


class TestOllamaAdapter(unittest.TestCase):
    """Test Ollama adapter."""
    
    @patch('adapters.ollama_adapter.requests.post')
    def test_execute(self, mock_post):
        """Test local inference."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "response": "Local model response",
            "eval_count": 5
        }
        mock_post.return_value = mock_response
        
        adapter = OllamaAdapter(base_url="http://localhost:11434")
        result = adapter.execute("Test", "llama3")
        
        self.assertEqual(result["response"], "Local model response")
        self.assertEqual(result["cost"], 0.0)  # Free


class TestFactory(unittest.TestCase):
    """Test adapter factory."""
    
    def test_get_adapter(self):
        """Test factory returns correct adapter."""
        adapter = get_adapter("openai", "key")
        self.assertIsInstance(adapter, OpenAIAdapter)
        
        adapter = get_adapter("ollama")
        self.assertIsInstance(adapter, OllamaAdapter)
    
    def test_invalid_provider(self):
        """Test invalid provider raises error."""
        with self.assertRaises(ValueError):
            get_adapter("invalid")


if __name__ == "__main__":
    unittest.main()
