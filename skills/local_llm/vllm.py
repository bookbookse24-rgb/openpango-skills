"""vLLM integration for high-performance local inference."""
import os, requests
from typing import Dict, Any, List

class VLLMClient:
    def __init__(self, base_url: str = ""):
        self.base_url = base_url or os.getenv("VLLM_URL", "http://localhost:8000")

    def generate(self, prompt: str, model: str = "meta-llama/Llama-3-8b", max_tokens: int = 512) -> Dict[str, Any]:
        try:
            r = requests.post(f"{self.base_url}/v1/completions",
                json={"model": model, "prompt": prompt, "max_tokens": max_tokens}, timeout=60)
            r.raise_for_status()
            return {"response": r.json()["choices"][0]["text"], "model": model}
        except Exception as e:
            return {"error": str(e)}

    def list_models(self) -> List[str]:
        try:
            r = requests.get(f"{self.base_url}/v1/models", timeout=10)
            return [m["id"] for m in r.json().get("data", [])]
        except:
            return []
