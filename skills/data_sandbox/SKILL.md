---
name: data-sandbox
description: "Jupyter-like sandboxed execution environment for data analysis tasks using pandas, numpy, and matplotlib."
version: "1.0.0"
user-invocable: true
metadata:
  capabilities:
    - data/analysis
    - data/visualization
    - data/csv-processing
  author: "Antigravity (OpenPango Core)"
  license: "MIT"
  dependencies:
    - pandas
    - numpy
    - matplotlib
---

# Data & Analytics Sandbox

A sandboxed code execution environment that allows OpenPango agents to run Python data analysis scripts in an isolated subprocess. This is the ecosystem's equivalent of a Jupyter notebook — but designed for fully autonomous agents rather than human operators.

## Features

- **Safe Execution**: Runs analysis code in a subprocess with resource limits and timeouts.
- **Standard Data Stack**: Full access to `pandas`, `numpy`, and `matplotlib` within the sandbox.
- **Structured Output**: Returns stdout, generated files (CSVs, PNGs), and execution metadata.
- **Mock Mode**: Falls back to simulated analysis when dependencies aren't installed.

## Usage

```python
from skills.data_sandbox.sandbox import DataSandbox

sandbox = DataSandbox()

result = sandbox.execute("""
import pandas as pd
import numpy as np

df = pd.DataFrame({
    'revenue': np.random.randint(1000, 5000, 12),
    'month': pd.date_range('2026-01', periods=12, freq='M')
})
print(df.describe().to_json())
""")

print(result["stdout"])  # JSON summary statistics
```
