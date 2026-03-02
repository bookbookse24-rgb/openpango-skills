# Metrics Skill

Tracks skill execution, API costs, and agent performance over time.

## Usage

```python
from skills.metrics import MetricsCollector, CostTracker

# Record execution
collector = MetricsCollector()
collector.start("my-skill")
# ... do work ...
collector.end("my-skill", duration_ms=1500, tokens=500, cost=0.02)

# Get cost report
tracker = CostTracker("~/.openclaw/workspace/metrics.jsonl")
tracker.print_report()
```

## CLI

```bash
python -m skills.metrics.cost_tracker
```
