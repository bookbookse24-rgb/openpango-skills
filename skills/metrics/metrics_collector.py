"""Metrics collector for skill execution events."""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

METRICS_FILE = os.getenv("METRICS_FILE", str(Path.home() / ".openclaw" / "workspace" / "metrics.jsonl"))

class MetricsCollector:
    """Records execution events (start, end, cost, tokens)."""
    
    def __init__(self, metrics_file: str = METRICS_FILE):
        self.metrics_file = Path(metrics_file)
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
    
    def record(self, event_type: str, skill_name: str, **kwargs):
        """Record a metric event."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,  # start, end, error
            "skill": skill_name,
            **kwargs
        }
        with open(self.metrics_file, "a") as f:
            f.write(json.dumps(event) + "\n")
    
    def start(self, skill_name: str, agent_id: Optional[str] = None):
        self.record("start", skill_name, agent_id=agent_id)
    
    def end(self, skill_name: str, duration_ms: int, tokens: int = 0, cost: float = 0.0, agent_id: Optional[str] = None):
        self.record("end", skill_name, duration_ms=duration_ms, tokens=tokens, cost=cost, agent_id=agent_id)
    
    def error(self, skill_name: str, error: str, agent_id: Optional[str] = None):
        self.record("error", skill_name, error=error, agent_id=agent_id)
