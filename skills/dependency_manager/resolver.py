import os
import yaml
import subprocess
import logging
from typing import Dict, List, Set, Any
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DependencyResolver")

class DependencyResolver:
    """
    OpenPango Core System Daemon: Skill Dependency Resolution.
    Parses SKILL.md dependencies and resolves the install graph to ensure 
    no cyclic or missing dependencies across the ecosystem.
    """
    
    def __init__(self, skills_dir: str = None):
        self.skills_dir = Path(skills_dir or os.path.expanduser("~/.openclaw/workspace/skills"))
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        # In this implementation, we simulate tracking the installed modules
        self._installed_packages: Set[str] = set()
        
    def _parse_skill_md(self, skill_path: Path) -> Dict[str, Any]:
        """Reads and parses the YAML frontmatter of a SKILL.md file."""
        skill_md_file = skill_path / "SKILL.md"
        if not skill_md_file.exists():
            return {}
            
        try:
            with open(skill_md_file, "r") as f:
                content = f.read()
                
            if content.startswith("---"):
                _, frontmatter, _ = content.split("---", 2)
                return yaml.safe_load(frontmatter) or {}
                
        except Exception as e:
            logger.error(f"Failed to parse frontmatter from {skill_md_file}: {e}")
            
        return {}
        
    def resolve_graph(self, target_skill: str, _visited: Set[str] = None) -> List[str]:
        """
        Calculates the flattened dependency graph for a target skill.
        Detects circular dependencies.
        """
        if _visited is None:
            _visited = set()
            
        if target_skill in _visited:
            raise ValueError(f"Circular dependency detected involving skill: {target_skill}")
            
        _visited.add(target_skill)
        
        info = self._parse_skill_md(self.skills_dir / target_skill)
        deps = info.get("dependencies", [])
        
        graph = []
        for dep in deps:
            sub_deps = self.resolve_graph(dep, _visited.copy())
            for sd in sub_deps:
                if sd not in graph:
                    graph.append(sd)
            if dep not in graph:
                graph.append(dep)
                
        return graph

    def install_dependencies(self, skill_name: str) -> bool:
        """
        Resolves the dependency graph and "installs" all requirements for a given skill.
        Normally this would invoke `pip install` or `npm install`.
        """
        logger.info(f"Resolving dependencies for skill: {skill_name}")
        
        try:
            graph = self.resolve_graph(skill_name)
        except ValueError as e:
            logger.error(f"Resolution failed: {e}")
            return False
            
        if not graph:
            logger.info("No external dependencies required.")
            return True
            
        logger.info(f"Dependency graph resolved: {' -> '.join(graph)}")
        
        for dep in graph:
            if dep not in self._installed_packages:
                logger.info(f"Attempting to install: {dep}")
                # Mock installation
                self._installed_packages.add(dep)
                logger.info(f"Successfully installed module: {dep}")
            else:
                logger.debug(f"Module {dep} is already installed.")
                
        return True

    def validate_workspace(self) -> List[str]:
        """
        Scans all skills in the workspace and verifies there are no broken dependencies.
        """
        errors = []
        if not self.skills_dir.exists():
            return errors
            
        for skill_dir in [d for d in self.skills_dir.iterdir() if d.is_dir()]:
            skill_name = skill_dir.name
            try:
                self.resolve_graph(skill_name)
            except ValueError as e:
                errors.append(str(e))
            except Exception as e:
                errors.append(f"Internal error validating {skill_name}: {e}")
                
        return errors

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Skill Dependency Resolver")
    parser.add_argument("--install", help="Install dependencies for a specific skill folder")
    parser.add_argument("--validate", action="store_true", help="Validate all installed skills")
    args = parser.parse_args()
    
    # Normally this would default to ~/.openclaw/workspace/skills
    resolver = DependencyResolver(skills_dir="./") 
    
    if args.install:
        success = resolver.install_dependencies(args.install)
        if not success:
            exit(1)
    elif args.validate:
        errors = resolver.validate_workspace()
        if errors:
            print("Workspace validation failed:")
            for err in errors:
                print(f"- {err}")
            exit(1)
        print("Workspace is valid. No dependency conflicts found.")
