"""Computer vision and multimodal analysis."""
import os, base64
from typing import Dict, Any, Optional

class ImageAnalyzer:
    def __init__(self, provider: str = "openai", api_key: str = ""):
        self.provider = provider
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

    def analyze(self, image_path: str, prompt: str = "Describe this image.") -> Dict[str, Any]:
        try:
            with open(image_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            import requests
            r = requests.post("https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": "gpt-4o", "messages": [{"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                ]}], "max_tokens": 300}, timeout=30)
            return {"description": r.json()["choices"][0]["message"]["content"]}
        except Exception as e:
            return {"error": str(e)}

    def detect_objects(self, image_path: str) -> Dict[str, Any]:
        return self.analyze(image_path, "List all objects visible in this image as JSON.")

    def extract_text(self, image_path: str) -> Dict[str, Any]:
        return self.analyze(image_path, "Extract all text visible in this image.")

def analyze_image(path: str, prompt: str = "Describe this image.") -> Dict[str, Any]:
    return ImageAnalyzer().analyze(path, prompt)
