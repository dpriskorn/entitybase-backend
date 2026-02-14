# Linter Best Practices

This document provides guidelines for creating custom linters in this project.

## When to Create a Custom Linter

Create a custom linter when:
- Enforcing project-specific patterns not covered by standard tools (ruff, mypy, etc.)
- Checking architectural constraints (e.g., "all API models must inherit from BaseModel")
- Detecting anti-patterns specific to this codebase (e.g., using `ValueError` instead of `raise_validation_error()`)

Do NOT create a custom linter for:
- Standard Python style issues → use **ruff**
- Type checking → use **mypy**
- Code complexity → use **radon**

## File Structure

All linters must follow this structure:

```python
#!/usr/bin/env python3
"""One-line description of what this linter checks."""

import ast
import sys
from pathlib import Path
from typing import List, Tuple

sys.path.append(str(Path(__file__).parent.resolve()))

from allowlist_utils import is_line_allowed

# Constants (e.g., excluded files, patterns)
EXCLUDED_FILES = {...}

def is_<check>(node: ast.AST) -> bool:
    ...

def check_file(file_path: Path, allowlist: set) -> List[Tuple[str, int, str, str]]:
    ...

def load_allowlist() -> set:
    ...

def main() -> int:
    ...

if __name__ == "__main__":
    sys.exit(main())
```

## Core Patterns

### AST-Based Checking

Use `ast.NodeVisitor` for traversing code:

```python
class MyChecker(ast.NodeVisitor):
    def __init__(self, file_path: str, allowlist: set):
        self.file_path = file_path
        self.allowlist = allowlist
        self.violations: List[Tuple[str, int, str, str]] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_function(node)
        self.generic_visit(node)
```

### Simple Function-Based Checking

For simpler checks, use `ast.walk()`:

```python
def check_file(file_path: Path) -> List[str]:
    errors = []
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if not is_valid_class(node):
                errors.append(f"{file_path}:{node.lineno}:1: Invalid class")
    return errors
```

## Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| File | `check_<what>.py` or `<what>_linter.py` | `check_dict_returns.py`, `value_error_linter.py` |
| Checker class | `<Purpose>Checker` | `DictReturnChecker`, `AnyReturnChecker` |
| Boolean functions | `is_<check>()`, `has_<attribute>()`, `should_<action>()` | `is_basemodel_subclass()`, `has_attributes()` |
| Main check function | `check_file()` | Always use this name |

## Error Format

Use this format for all error messages:

```
{file_path}:{line_number}:1: {description}
```

Example:
```python
errors.append(f"{file_path}:{node.lineno}:1: Class '{node.name}' does not inherit from BaseModel")
```

For violations with suggestions:
```python
errors.append(
    f"{file_path}:{node.lineno}:1: Replace 'raise ValueError(...)' with 'raise_validation_error(...)'"
)
```

## Skipping Files

Standard patterns to exclude:

```python
for py_file in src_dir.rglob("*.py"):
    if "tests" in py_file.parts or "scripts" in py_file.parts:
        continue
    if py_file.name.startswith("test_"):
        continue
    if "workers" in py_file.parts:
        continue
```

For file-level exclusions:
```python
EXCLUDED_FILES = {
    "models/services/wikidata_import_service.py",
    "models/rest_api/utils.py",
}
```

## Allowlists

### Format

Allowlist files live in `config/linters/allowlists/custom/<linter-name>.txt`:

```
# Line-specific (with tolerance of ±2 lines)
src/models/api/response.py:42
src/models/api/request.py:15

# File-wide (entire file excluded)
src/models/internal/legacy.py
```

### Loading Allowlist

```python
def load_allowlist() -> set:
    """Load the allowlist from config/linters/allowlists/custom/<name>.txt."""
    allowlist_path = Path("config/linters/allowlists/custom/my-linter.txt")
    allowlist = set()
    if allowlist_path.exists():
        with open(allowlist_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    allowlist.add(line)
    return allowlist
```

### Using Allowlist

```python
from allowlist_utils import is_line_allowed

if is_line_allowed(self.file_path, node.lineno, self.allowlist):
    return  # Skip this violation
```

The `is_line_allowed()` function has a default tolerance of ±2 lines to handle minor code changes.

## Full Template

Copy this template for new linters:

```python
#!/usr/bin/env python3
"""Linter to check for <description of what this checks>."""

import ast
import sys
from pathlib import Path
from typing import List, Tuple

sys.path.append(str(Path(__file__).parent.resolve()))

from allowlist_utils import is_line_allowed

EXCLUDED_FILES: set[str] = set()


class ViolationChecker(ast.NodeVisitor):
    """AST visitor to check for <violations>."""

    def __init__(self, file_path: str, allowlist: set[str]):
        self.file_path = file_path
        self.allowlist = allowlist
        self.violations: List[Tuple[str, int, str, str]] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_function(node)
        self.generic_visit(node)

    def _check_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        if is_line_allowed(self.file_path, node.lineno, self.allowlist):
            return
        # Add your check logic here
        if self._is_violation(node):
            self.violations.append(
                (
                    node.name,
                    node.lineno,
                    f"Function '{node.name}' violates rule",
                    str(self.file_path),
                )
            )

    def _is_violation(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        # Implement your check
        return False


def check_file(file_path: Path, allowlist: set[str]) -> List[Tuple[str, int, str, str]]:
    """Check a single Python file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source, filename=str(file_path))
        checker = ViolationChecker(str(file_path), allowlist)
        checker.visit(tree)
        return checker.violations
    except SyntaxError:
        return [(str(file_path), 0, f"Syntax error in {file_path}", str(file_path))]


def load_allowlist() -> set[str]:
    """Load the allowlist from config/linters/allowlists/custom/<name>.txt."""
    allowlist_path = Path("config/linters/allowlists/custom/my-linter.txt")
    if not allowlist_path.exists():
        return set()
    with open(allowlist_path, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip() and not line.startswith("#")}


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python my_linter.py <path>")
        return 1

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Path {path} does not exist")
        return 1

    allowlist = load_allowlist()
    violations = []

    if path.is_file() and path.suffix == ".py":
        violations.extend(check_file(path, allowlist))
    elif path.is_dir():
        for py_file in path.rglob("*.py"):
            if "tests" in py_file.parts or "scripts" in py_file.parts:
                continue
            if py_file.name.startswith("test_"):
                continue
            violations.extend(check_file(py_file, allowlist))

    if violations:
        for func_name, line_no, message, file_path in violations:
            print(f"{file_path}:{line_no}: {message}")
        return 1

    print("No violations found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## Disabled Linters

Move linters to `scripts/linters/disabled/` when:
- The check is no longer relevant (e.g., migration complete)
- The linter causes too many false positives
- The check is being replaced by a standard tool

Keep disabled linters for reference rather than deleting them.

## Testing Linters

Create test cases for your linter:

```python
def test_my_linter_detects_violation():
    from scripts.linters.my_linter import check_file
    violations = check_file(Path("tests/fixtures/violation_example.py"), set())
    assert len(violations) == 1
    assert "violation message" in violations[0][2]

def test_my_linter_passes_clean_file():
    from scripts.linters.my_linter import check_file
    violations = check_file(Path("tests/fixtures/clean_example.py"), set())
    assert len(violations) == 0
```

## Existing Linters Reference

| Linter | Purpose | Pattern |
|--------|---------|---------|
| `value_error_linter.py` | Detect `raise ValueError()` → `raise_validation_error()` | Simple `ast.walk()` |
| `check_dict_returns.py` | Detect `-> dict` return types | `NodeVisitor` + allowlist |
| `check_any_returns.py` | Detect `-> Any` return types | `NodeVisitor` + allowlist |
| `basemodel_linter.py` | Ensure classes inherit from BaseModel | `ast.walk()` + class checks |
| `check_long_files.py` | Check file line counts | File iteration (no AST) |
