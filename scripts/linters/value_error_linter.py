#!/usr/bin/env python3
"""Linter to check for raise ValueError() that should be raise_validation_error()."""

import ast
import sys
from pathlib import Path
from typing import List


# Files to skip (ValueError appropriate here)
EXCLUDED_FILES = {
    "models/services/wikidata_import_service.py",
    "models/internal_representation/values/quantity_value.py",
    "models/rest_api/utils.py",
}


def is_value_error_raise(node: ast.Raise) -> bool:
    """Check if a raise statement is raising ValueError."""
    if node.exc is None:
        return False
    if isinstance(node.exc, ast.Name) and node.exc.id == "ValueError":
        return True
    if (
        isinstance(node.exc, ast.Call)
        and isinstance(node.exc.func, ast.Name)
        and node.exc.func.id == "ValueError"
    ):
        return True
    return False


def get_value_error_message(node: ast.Raise) -> str:
    """Extract the message from ValueError(...)."""
    if isinstance(node.exc, ast.Call) and node.exc.args:
        arg = node.exc.args[0]
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            return arg.value
    return ""


def should_check_file(file_path: Path) -> bool:
    """Check if file should be linted (focus on user-facing code)."""
    relative_path = str(file_path.relative_to(Path("src")))
    # Skip excluded files
    if relative_path in EXCLUDED_FILES:
        return False
    # Prioritize rest_api and infrastructure
    return "rest_api" in relative_path or "infrastructure" in relative_path


def check_file(file_path: Path) -> List[str]:
    """Check a file for raise ValueError() statements."""
    errors = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content, filename=str(file_path))
    except SyntaxError:
        return [f"{file_path}:1:1: E999 SyntaxError in file"]

    for node in ast.walk(tree):
        if isinstance(node, ast.Raise) and is_value_error_raise(node):
            message = get_value_error_message(node)
            suggestion = (
                f"raise_validation_error('{message}', status_code=400)"
                if message
                else "raise_validation_error(..., status_code=400)"
            )
            errors.append(
                f"{file_path}:{node.lineno}:1: Replace 'raise ValueError(...)' with '{suggestion}'"
            )

    return errors


def main() -> int:
    """Main entry point."""
    src_dir = Path("src")
    if not src_dir.exists():
        print("Error: src/ directory not found", file=sys.stderr)
        return 1

    all_errors = []
    for py_file in src_dir.rglob("*.py"):
        # Skip tests and scripts
        if "tests" in py_file.parts or "scripts" in py_file.parts:
            continue
        if not should_check_file(py_file):
            continue
        errors = check_file(py_file)
        all_errors.extend(errors)

    for error in all_errors:
        print(error)

    return 1 if all_errors else 0


if __name__ == "__main__":
    sys.exit(main())
