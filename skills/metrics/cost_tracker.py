"""Cost tracker - aggregates costs by skill, agent, time period."""

import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Any

class CostTracker:
    """Aggregates and reports metrics."""
    
    def __init__(self, metrics_file: str):
        self.metrics_file = Path(metrics_file)
    
    def load_events(self) -> List[Dict]:
        """Load all events from metrics file."""
        if not self.metrics_file.exists():
            return []
        events = []
        with open(self.metrics_file) as f:
            for line in f:
                try:
                    events.append(json.loads(line))
                except:
                    pass
        return events
    
    def get_totals(self, hours: int = 24) -> Dict[str, Any]:
        """Get totals for the last N hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        events = self.load_events()
        
        stats = defaultdict(lambda: {"executions": 0, "errors": 0, "tokens": 0, "cost": 0.0, "total_time_ms": 0})
        
        for e in events:
            try:
                ts = datetime.fromisoformat(e.get("timestamp", ""))
                if ts < cutoff:
                    continue
                skill = e.get("skill", "unknown")
                if e.get("type") == "end":
                    stats[skill]["executions"] += 1
                    stats[skill]["tokens"] += e.get("tokens", 0)
                    stats[skill]["cost"] += e.get("cost", 0.0)
                    stats[skill]["total_time_ms"] += e.get("duration_ms", 0)
                elif e.get("type") == "error":
                    stats[skill]["errors"] += 1
            except:
                pass
        
        return dict(stats)
    
    def print_report(self):
        """Print color-coded report."""
        totals = self.get_totals()
        
        print("\n📊 Skill Execution Report (24h)")
        print("=" * 60)
        print(f"{'Skill':<25} {'Runs':>6} {'Errors':>7} {'Tokens':>10} {'Cost':>10}")
        print("-" * 60)
        
        total_cost = 0
        for skill, data in sorted(totals.items(), key=lambda x: -x[1]["cost"]):
            cost = data["cost"]
            total_cost += cost
            runs = data["executions"]
            errs = data["errors"]
            toks = data["tokens"]
            err_color = "\033[91m" if errs > 0 else ""
            reset = "\033[0m"
            print(f"{skill:<25} {runs:>6} {err_color}{errs:>7}{reset} {toks:>10} ${cost:>9.4f}")
        
        print("-" * 60)
        print(f"{'TOTAL':<25} {sum(d['executions'] for d in totals.values()):>6} {sum(d['errors'] for d in totals.values()):>7} {sum(d['tokens'] for d in totals.values()):>10} ${total_cost:>9.4f}")

if __name__ == "__main__":
    from pathlib import Path
    home = Path.home()
    tracker = CostTracker(str(home / ".openclaw" / "workspace" / "metrics.jsonl"))
    tracker.print_report()
