---
name: figma
description: "Figma API integration for design-to-code translation."
user-invocable: true
metadata: {"openclaw":{"emoji":"🎨","skillKey":"openpango-figma"}}
---

## Cross-Skill Integration

This skill integrates with the Openpango ecosystem:
- **Orchestration**: Orchestration can delegate design-to-code tasks to this skill.
- **Frontend-Design**: Extracted styles and DOM structures feed into the frontend-design skill for code generation.
- **Self-Improvement**: Errors are logged by the self-improvement skill.
- **Persistent State**: Shared workspace files at `~/.openclaw/workspace/`.

# Figma Design-to-Code Skill

Extract design tokens, styles, and structural information from Figma files and translate them into code-ready formats.

## Setup

Set your Figma API token:
```bash
export FIGMA_ACCESS_TOKEN="your-figma-personal-access-token"
```

Or configure via OpenPango CLI:
```bash
openpango config set figma.token YOUR_TOKEN
```

## Usage

### Extract Node Styles
```python
from skills.figma.figma_reader import FigmaReader

reader = FigmaReader(token="your-token")
styles = reader.extract_node_styles("file_id", "node_id")
# Returns CSS-like style dict: {"width": "320px", "background": "#FF5733", ...}
```

### Export Assets
```python
assets = reader.export_assets("file_id", "node_id", format="svg", scale=2)
# Returns list of {"node_id": "...", "url": "https://...", "format": "svg"}
```

### Parse Full Design Tree
```python
dom = reader.parse_design_tree("file_id", "node_id")
# Returns simplified DOM-like structure:
# {"tag": "div", "class": "flex flex-col gap-4 p-6", "children": [...]}
```

## Tools Available to Agents

| Tool | Description |
|------|-------------|
| `extract_node_styles(file_id, node_id)` | Get CSS-like styles for any Figma node |
| `export_assets(file_id, node_id)` | Export images/SVGs from Figma |
| `parse_design_tree(file_id, node_id)` | Convert Figma tree to simplified DOM |
| `list_components(file_id)` | List all reusable components in a file |
| `get_design_tokens(file_id)` | Extract color, typography, and spacing tokens |
