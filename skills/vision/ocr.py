"""OCR using Tesseract or API."""
import os
from typing import Dict, Any

class OCR:
    def extract(self, image_path: str) -> Dict[str, Any]:
        try:
            import pytesseract
            from PIL import Image
            text = pytesseract.image_to_string(Image.open(image_path))
            return {"text": text.strip(), "engine": "tesseract"}
        except Exception:
            from .image_analyzer import ImageAnalyzer
            return ImageAnalyzer().extract_text(image_path)

def extract_text(image_path: str) -> str:
    return OCR().extract(image_path).get("text", "")
