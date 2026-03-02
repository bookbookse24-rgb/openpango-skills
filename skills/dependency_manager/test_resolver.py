import pytest
import os
import tempfile
import textwrap
from pathlib import Path
from skills.dependency_manager.resolver import DependencyResolver

@pytest.fixture
def mock_skills_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir = Path(tmpdir)
        
        # Skill A depends on B and C
        a_dir = base_dir / "skill-a"
        a_dir.mkdir()
        with open(a_dir / "SKILL.md", "w") as f:
            f.write(textwrap.dedent("""\
            ---
            name: skill-a
            dependencies:
              - skill-b
              - skill-c
            ---
            """))
            
        # Skill B depends on D
        b_dir = base_dir / "skill-b"
        b_dir.mkdir()
        with open(b_dir / "SKILL.md", "w") as f:
            f.write(textwrap.dedent("""\
            ---
            name: skill-b
            dependencies:
              - skill-d
            ---
            """))
            
        # Skill C depends on D
        c_dir = base_dir / "skill-c"
        c_dir.mkdir()
        with open(c_dir / "SKILL.md", "w") as f:
            f.write(textwrap.dedent("""\
            ---
            name: skill-c
            dependencies:
              - skill-d
            ---
            """))
            
        # Skill D has no dependencies
        d_dir = base_dir / "skill-d"
        d_dir.mkdir()
        with open(d_dir / "SKILL.md", "w") as f:
            f.write(textwrap.dedent("""\
            ---
            name: skill-d
            dependencies: []
            ---
            """))
            
        # Skill E (Circular dependency with F)
        e_dir = base_dir / "skill-e"
        e_dir.mkdir()
        with open(e_dir / "SKILL.md", "w") as f:
            f.write(textwrap.dedent("""\
            ---
            name: skill-e
            dependencies:
              - skill-f
            ---
            """))
            
        f_dir = base_dir / "skill-f"
        f_dir.mkdir()
        with open(f_dir / "SKILL.md", "w") as f:
            f.write(textwrap.dedent("""\
            ---
            name: skill-f
            dependencies:
              - skill-e
            ---
            """))
            
        yield base_dir

def test_acyclic_dependency_resolution(mock_skills_dir):
    resolver = DependencyResolver(skills_dir=mock_skills_dir)
    graph = resolver.resolve_graph("skill-a")
    
    # Expected resolution:
    # A -> B -> D
    # A -> C -> D
    # Order: D, B, C (or D, C, B)
    assert len(graph) == 3
    assert "skill-d" in graph
    assert "skill-b" in graph
    assert "skill-c" in graph
    
    # D must be resolved before B and C
    d_index = graph.index("skill-d")
    b_index = graph.index("skill-b")
    c_index = graph.index("skill-c")
    assert d_index < b_index
    assert d_index < c_index

def test_circular_dependency_detection(mock_skills_dir):
    resolver = DependencyResolver(skills_dir=mock_skills_dir)
    with pytest.raises(ValueError, match="Circular dependency detected"):
        resolver.resolve_graph("skill-e")

def test_missing_dependency(mock_skills_dir):
    # A missing dependency just resolves to an empty frontmatter, returning no further deps.
    # The actual graph will include the missing dependency string so the installer can try to fetch it.
    resolver = DependencyResolver(skills_dir=mock_skills_dir)
    
    # Let's dynamically add a skill-g that depends on missing-skill
    g_dir = mock_skills_dir / "skill-g"
    g_dir.mkdir()
    with open(g_dir / "SKILL.md", "w") as f:
        f.write(textwrap.dedent("""\
        ---
        name: skill-g
        dependencies:
          - missing-skill
        ---
        """))
        
    graph = resolver.resolve_graph("skill-g")
    assert graph == ["missing-skill"]

def test_validate_workspace(mock_skills_dir):
    resolver = DependencyResolver(skills_dir=mock_skills_dir)
    errors = resolver.validate_workspace()
    
    # Should catch the circular dependency in E and F
    assert any("skill-e" in err or "skill-f" in err for err in errors)
    assert len(errors) == 2 # one for E failing, one for F failing
