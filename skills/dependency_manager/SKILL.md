---
name: "Skill Dependency Manager"
description: "Resolves, installs, and validates transitive dependencies for OpenPango skills to prevent missing modules."
version: "1.0.0"
user-invocable: false
system-daemon: true
metadata:
  capabilities:
    - system/dependency-resolution
    - packaging/install
  author: "Antigravity (OpenPango Core)"
  license: "MIT"
---

# Skill Dependency Manager

As the A2A economy scales and agents dynamically download skills from the decentralized registry, managing transitive dependencies is critical. This daemon resolves dependencies declared in a `SKILL.md` frontmatter, checks for conflicts, and securely installs them using `npm` or `pip` within the skill's isolated environment.

## Features
- **Dependency Graph Resolution:** Detects circular dependencies and conflicts.
- **Auto-Installation:** Seamlessly installs missing `dependencies` required by a downloaded skill.
- **Validation:** Verifies that existing environments satisfy constraints.

## Usage

```python
from skills.dependency_manager.resolver import DependencyResolver

resolver = DependencyResolver(skills_dir="/path/to/openpango/skills")

# Resolve and install dependencies for a specifically downloaded skill
resolver.install_dependencies("new-scraper-skill")

# Validate the entire dependency graph across all installed skills
errors = resolver.validate_workspace()
if errors:
    print(f"Graph Errors: {errors}")
```
