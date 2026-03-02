"""Ollama local LLM integration."""
import os, json, requests
from typing import Dict, Any, List, Optional

class OllamaClient:
    def __init__(self, base_url: str = ""):
        self.base_url = base_url or os.getenv("OLLAMA_URL", "http://localhost:11434")

    def generate(self, prompt: str, model: str = "llama3", stream: bool = False) -> Dict[str, Any]:
        try:
            r = requests.post(f"{self.base_url}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False}, timeout=60)
            r.raise_for_status()
            data = r.json()
            return {"response": data.get("response"), "model": model, "done": data.get("done", True)}
        except Exception as e:
            return {"error": str(e)}

    def list_models(self) -> List[str]:
        try:
            r = requests.get(f"{self.base_url}/api/tags", timeout=10)
            return [m["name"] for m in r.json().get("models", [])]
        except:
            return []

    def chat(self, messages: List[Dict], model: str = "llama3") -> Dict[str, Any]:
        try:
            r = requests.post(f"{self.base_url}/api/chat",
                json={"model": model, "messages": messages, "stream": False}, timeout=60)
            r.raise_for_status()
            return r.json().get("message", {})
        except Exception as e:
            return {"error": str(e)}

def ask_ollama(prompt: str, model: str = "llama3") -> str:
    result = OllamaClient().generate(prompt, model)
    return result.get("response", result.get("error", ""))
