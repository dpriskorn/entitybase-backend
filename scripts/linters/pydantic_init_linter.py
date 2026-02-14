#!/usr/bin/env python3
"""Linter to check for __init__ methods in Pydantic BaseModel subclasses, suggesting model_post_init instead."""

import ast
import sys
from pathlib import Path
from typing import List

sys.path.append(str(Path(__file__).parent.resolve()))

from allowlist_utils import is_line_allowed


def check_file(file_path: Path, allowlist: set) -> List[str]:
    """Check a file for __init__ methods in classes."""
    errors = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content, filename=str(file_path))
    except SyntaxError:
        return [f"{file_path}:1:1: E999 SyntaxError in file"]

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "__init__":
            if is_line_allowed(str(file_path), node.lineno, allowlist):
                continue
            # Find the class name
            class_name = None
            for parent in ast.walk(tree):
                if isinstance(parent, ast.ClassDef) and node in parent.body:
                    class_name = parent.name
                    break
            if class_name:
                errors.append(
                    f"{file_path}:{node.lineno}:1: Class '{class_name}' defines __init__. Consider using model_post_init if it's a Pydantic model."
                )

    return errors


def load_allowlist() -> set:
    """Load the allowlist from config/linters/allowlists/custom/pydantic-init.txt."""
    allowlist_path = Path("config/linters/allowlists/custom/pydantic-init.txt")
    allowlist = set()
    if allowlist_path.exists():
        with open(allowlist_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    allowlist.add(line)
    return allowlist


def main() -> int:
    """Main entry point."""
    src_dir = Path("src")
    if not src_dir.exists():
        import sys

        print("Error: src/ directory not found", file=sys.stderr)
        return 1

    allowlist = load_allowlist()
    all_errors = []
    for py_file in src_dir.rglob("*.py"):
        if "tests" in py_file.parts or "__pycache__" in py_file.parts:
            continue
        errors = check_file(py_file, allowlist)
        all_errors.extend(errors)

    for error in all_errors:
        print(error)

    return 1 if all_errors else 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
