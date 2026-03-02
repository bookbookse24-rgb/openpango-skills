"""Manage agent personality/soul customization."""
import os, json
from pathlib import Path
from typing import Dict, Any, Optional

SOUL_PATH = os.getenv("SOUL_PATH", str(Path.home() / ".openclaw" / "workspace" / "SOUL.md"))

class SoulManager:
    def __init__(self, soul_path: str = SOUL_PATH):
        self.soul_path = soul_path

    def get(self) -> str:
        if Path(self.soul_path).exists():
            return Path(self.soul_path).read_text()
        return ""

    def set(self, soul_content: str) -> Dict[str, Any]:
        Path(self.soul_path).write_text(soul_content)
        return {"updated": True, "path": self.soul_path}

    def update_trait(self, trait: str, value: str) -> Dict[str, Any]:
        soul = self.get()
        lines = soul.split("\n")
        for i, line in enumerate(lines):
            if trait.lower() in line.lower():
                lines[i] = f"{trait}: {value}"
                break
        else:
            lines.append(f"\n## {trait}\n{value}")
        updated = "\n".join(lines)
        return self.set(updated)

    def get_traits(self) -> Dict[str, str]:
        soul = self.get()
        traits = {}
        for line in soul.split("\n"):
            if ": " in line and not line.startswith("#"):
                k, _, v = line.partition(": ")
                traits[k.strip()] = v.strip()
        return traits

def get_soul() -> str:
    return SoulManager().get()

def set_soul(content: str) -> Dict[str, Any]:
    return SoulManager().set(content)
