"""Handle GitHub App webhooks for CI/CD."""

import hmac
import hashlib
import json
from typing import Dict, Any, Optional
from datetime import datetime

class WebhookHandler:
    """Process GitHub App webhooks securely."""
    
    def __init__(self, secret: str = "", app_id: str = ""):
        self.secret = secret
        self.app_id = app_id
    
    def verify(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature."""
        if not self.secret:
            return True
        expected = hmac.new(
            self.secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(f"sha256={expected}", signature)
    
    def handle(self, event: str, payload: Dict) -> Dict[str, Any]:
        """Handle incoming webhook."""
        handlers = {
            "push": self._handle_push,
            "pull_request": self._handle_pr,
            "issues": self._handle_issue,
            "check_run": self._handle_check,
        }
        handler = handlers.get(event, self._handle_default)
        return handler(payload)
    
    def _handle_push(self, payload: Dict) -> Dict[str, Any]:
        return {
            "event": "push",
            "repo": payload.get("repository", {}).get("full_name"),
            "branch": payload.get("ref", "").split("/")[-1],
            "commits": len(payload.get("commits", []))
        }
    
    def _handle_pr(self, payload: Dict) -> Dict[str, Any]:
        pr = payload.get("pull_request", {})
        return {
            "event": "pull_request",
            "action": payload.get("action"),
            "repo": payload.get("repository", {}).get("full_name"),
            "pr_number": pr.get("number"),
            "title": pr.get("title")
        }
    
    def _handle_issue(self, payload: Dict) -> Dict[str, Any]:
        return {"event": "issues", "action": payload.get("action")}
    
    def _handle_check(self, payload: Dict) -> Dict[str, Any]:
        return {"event": "check_run", "status": payload.get("action")}
    
    def _handle_default(self, payload: Dict) -> Dict[str, Any]:
        return {"event": "unknown", "received": True}

# Tool functions
def handle_webhook(event: str, payload: Dict, secret: str = "") -> Dict[str, Any]:
    """Handle GitHub webhook."""
    return WebhookHandler(secret).handle(event, payload)
