---
name: echo13-development
description: "ECHO-13 development guidelines. Use when implementing features, fixes, or tests for the ECHO-13 engine, graph, or examples. Enforces type hints, deterministic behavior, history preservation, and quality-first workflow."
applyTo: "echo13/**/*.py tests/**/*.py examples/**/*.py"
---

# ECHO-13 Development Instructions

Guidelines for working on ECHO-13: a deterministic symbolic language for modeling continuous unfolding through entities, traces, relational dynamics, braids, and non-destructive Soft Overlap Compression (SOR).

## Rule Precedence

When requirements conflict, apply them in this order:
1. **Correctness and determinism** – changes must preserve deterministic behavior and historical traces.
2. **History preservation** – never overwrite or delete accumulated traces without explicit justification.
3. **Minimal dependencies** – avoid new external libraries; suggest alternatives before adding imports.
4. **Style and documentation** – type hints, docstrings, and code organization.

If a change cannot satisfy the top priority without compromising a lower priority, stop and explain the blocker instead of proceeding with a partial solution.

## Core Principles

1. **Determinism**: All behavior must be reproducible. Use `seed` in `EngineConfig` and avoid non-deterministic operations (e.g., `random.random()` without seeding). If a requested change cannot be made deterministic without adding a new dependency or using non-seeded randomness, stop and explain the blocker instead of guessing.
2. **History Preservation**: Traces and records accumulate; never overwrite or delete historical data without explicit justification.
3. **Minimal Dependencies**: Keep the engine dependency-free and lightweight for easy portability and study. If a requested change requires a new dependency or non-deterministic behavior, explain why and ask for approval before proceeding.
4. **Type Safety**: All functions and methods in `echo13/**/*.py` and `tests/**/*.py`, including private helpers, must have type annotations. Public APIs must also have docstrings.

## Code Style

### Type Hints (Required)
All functions and methods, including private helpers, must have type annotations:
```python
def update_entity(entity: Entity, delta_t: float) -> None:
    """Update entity position and state."""
    pass

def _compute_distance(p1: tuple[float, float], p2: tuple[float, float]) -> float:
    """Euclidean distance between two points (private helper)."""
    pass
```

Use `TYPE_CHECKING` only for imports that are needed only in annotations and would create a runtime circular import; otherwise use a normal import:
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from echo13.graph import SymbolGraph  # Imported only for type hints
```

### Docstrings (Required)
Use triple-quoted docstrings with NumPy/SciPy style for public APIs:
```python
def evolve(self, iterations: int) -> None:
    """
    Evolve the engine for N iterations.

    Parameters
    ----------
    iterations : int
        Number of update cycles to perform.

    Raises
    ------
    ValueError
        If iterations < 1.
    """
    pass
```

### Comments
Use section dividers for major logical blocks:
```python
# ── Entity Updates ──────────────────────────────────────────────────

def update_entities(self) -> None:
    """Update all entities in the graph."""
    pass
```

### Dataclasses
Prefer dataclasses with clear field defaults:
```python
from dataclasses import dataclass, field

@dataclass
class EngineConfig:
    """Configuration for an ECHO-13 engine session."""
    recursion_depth: int = 1
    mutation_rate: float = 0.0
    seed: int = 42
    enable_tracing: bool = False
```

## Modifying Existing Code

When editing existing code that violates these guidelines:
- Add missing type hints and docstrings only to the functions you modify.
- Do not refactor unrelated files unless the task explicitly requires it.
- If you encounter pervasive violations (e.g., entire module lacks type hints), note it in your commit message and discuss with maintainers before proceeding.

## Testing Requirements

### Write Tests First (TDD)
1. Define the behavior you want.
2. Write a failing test.
3. Implement the feature.
4. Verify all tests pass. If tests cannot run in the current environment, report the exact failure or missing dependency and do not claim the change is verified.

### Test Organization
- Place tests in `tests/` directory.
- Use class-based organization: `class TestFeatureName:`
- One logical concern per test method.

### Test Example
```python
class TestEntityUpdate:
    """Tests for entity position and state updates."""

    def test_entity_moves_with_tempo(self) -> None:
        """Entity position increases by tempo each step."""
        entity = Entity(position=(0.0, 0.0), tempo=1.5)
        entity.update(delta_t=1.0)
        assert entity.position[0] == 1.5

    def test_entity_preserves_history(self) -> None:
        """Entity history trace is never overwritten."""
        entity = Entity(position=(0.0, 0.0))
        old_pos = (0.0, 0.0)
        entity.update(delta_t=1.0)
        new_pos = entity.position
        assert old_pos in entity.history  # History preserved
        assert old_pos != new_pos
```

### Run Tests
```bash
# All tests
pytest

# With coverage
pytest --cov=echo13 --cov=examples --cov-report=html

# Specific test class
pytest tests/test_basic.py::TestEngineConfig

# Verbose output
pytest -v
```

If any test fails, do not mark the task complete; fix the failure or report the exact blocker with the failing test name and error message.

### Test Markers
Use markers with clear policies:
- `@pytest.mark.slow`: Tests that take longer than 1 second or require large data (e.g., 1000+ iterations).
- `@pytest.mark.conda`: Tests that require the conda/scipy/numpy stack (not available in base environment).

```python
import pytest

@pytest.mark.slow
def test_large_graph_evolution() -> None:
    """Simulate large graph over 1000 iterations."""
    pass

@pytest.mark.conda
def test_with_scientific_stack() -> None:
    """Test that requires scipy or numpy."""
    pass
```

Run selectively:
```bash
pytest -m "not slow"  # Skip slow tests
pytest -m conda       # Run only conda-specific tests
```

## Determinism & Testing

### Seed Everything
Always set seeds in tests to ensure reproducibility:
```python
def test_deterministic_evolution() -> None:
    config = EngineConfig(seed=42)
    session1 = Session(config, graph1)
    session1.evolve(10)
    
    config2 = EngineConfig(seed=42)
    session2 = Session(config2, graph1)
    session2.evolve(10)
    
    assert session1.trace == session2.trace  # Identical evolution
```

### No Random Side Effects
Avoid random operations outside of seeded contexts:
```python
# ❌ Bad: non-deterministic
import random
def update(self):
    self.value = random.random()  # Not seeded

# ✓ Good: uses seeded RNG
def update(self):
    self.value = self._rng.random()  # Uses session's seeded RNG
```

## Commits & Pull Requests

Follow the **quality-first-workflow** skill:

1. **Write & test** before committing.
2. **One logical change per commit**:
   ```
   feat: add Entity.tempo attribute and update logic
   fix: prevent trace overwrite in Session.evolve()
   test: add determinism check for 100-iteration evolution
   refactor: consolidate distance calculations into shared method
   ```
3. **Descriptive PR title**: `feat: implement Soft Overlap Compression (SOR)`
4. **Link issues**: `Closes #42` in PR description.
5. **Thorough review**: 
   - Do traces accumulate correctly?
   - Is determinism preserved?
   - Are type hints complete?
   - Do all tests pass?

## Common Patterns

### History & Trace Accumulation
```python
@dataclass
class Entity:
    position: tuple[float, float]
    history: list[tuple[float, float]] = field(default_factory=list)
    
    def update(self, delta_t: float) -> None:
        """Record old position before updating."""
        self.history.append(self.position)  # Accumulate, never delete
        self.position = (self.position[0] + self.tempo * delta_t, self.position[1])
```

### Relational Dynamics
```python
def compute_synchrony(entity_a: Entity, entity_b: Entity) -> float:
    """
    Compute synchrony between two entities based on distance.
    
    Closer entities → higher synchrony (mutual influence).
    """
    dist = distance(entity_a.position, entity_b.position)
    return max(0.0, 1.0 - dist / MAX_DISTANCE)
```

### Session Configuration Validation
```python
def __post_init__(self) -> None:
    """Validate configuration after dataclass initialization."""
    if self.recursion_depth < 1:
        raise ValueError("recursion_depth must be >= 1")
    if not (0.0 <= self.mutation_rate <= 1.0):
        raise ValueError("mutation_rate must be between 0.0 and 1.0")
```

## Documentation

- **Code**: Add docstrings to all public classes/functions.
- **Examples**: Place in `examples/` with clear descriptions (see `02_parameter_variation.py`, `03_trace_inspection.py`).
- **Architecture**: Update `docs/` for major structural changes.
- **README**: Keep high-level overview; link to docs for details.

## Review Checklist

Before submitting a PR, ensure:
- [ ] All new code has type hints.
- [ ] All public APIs have docstrings.
- [ ] Tests pass: `pytest --cov`
- [ ] No history overwritten (trace/record design intentional?).
- [ ] Determinism verified with fixed seed.
- [ ] Commit messages are concise and focused.
- [ ] No external dependencies added without justification.
- [ ] Examples run without error.

## Quick Start for Contributors

```bash
# Clone and install in development mode
git clone https://github.com/Octoous72/ECHO-13-Theoretic-Language-Program.git
cd ECHO-13-Theoretic-Language-Program
pip install -e .

# Run tests
pytest --cov

# Run an example
python examples/02_parameter_variation.py

# Create a feature branch
git checkout -b feat/my-feature

# Make changes, test, commit, push, and open a PR
```

