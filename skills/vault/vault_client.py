"""HashiCorp Vault integration for enterprise secrets management."""
import os, json
from typing import Dict, Any, Optional

class VaultClient:
    def __init__(self, url: str = "", token: str = ""):
        self.url = url or os.getenv("VAULT_ADDR", "http://localhost:8200")
        self.token = token or os.getenv("VAULT_TOKEN")

    def _headers(self):
        return {"X-Vault-Token": self.token or "", "Content-Type": "application/json"}

    def get_secret(self, path: str, key: str = "") -> Dict[str, Any]:
        """Read secret from Vault KV store."""
        try:
            import requests
            r = requests.get(f"{self.url}/v1/secret/data/{path}", headers=self._headers(), timeout=10)
            data = r.json().get("data", {}).get("data", {})
            return {"value": data.get(key) if key else data, "path": path}
        except Exception as e:
            return {"error": str(e)}

    def set_secret(self, path: str, data: Dict) -> Dict[str, Any]:
        try:
            import requests
            r = requests.post(f"{self.url}/v1/secret/data/{path}",
                headers=self._headers(), json={"data": data}, timeout=10)
            return {"written": r.status_code == 200, "path": path}
        except Exception as e:
            return {"error": str(e)}

    def list_secrets(self, path: str = "") -> Dict[str, Any]:
        try:
            import requests
            r = requests.request("LIST", f"{self.url}/v1/secret/metadata/{path}",
                headers=self._headers(), timeout=10)
            return {"keys": r.json().get("data", {}).get("keys", []), "path": path}
        except Exception as e:
            return {"error": str(e)}

def get_secret(path: str, key: str = "") -> Dict[str, Any]:
    return VaultClient().get_secret(path, key)

def set_secret(path: str, data: Dict) -> Dict[str, Any]:
    return VaultClient().set_secret(path, data)
