#!/usr/bin/env python3
"""Linter to check for functions returning dict types instead of pydantic models."""

import ast
from pathlib import Path
from typing import List


def has_dict_return_annotation(node: ast.FunctionDef) -> bool:
    """Check if a function has a return annotation containing dict[...]."""
    if node.returns is None:
        return False

    # Convert the annotation to string and check for dict[
    annotation_str = (
        ast.unparse(node.returns) if hasattr(ast, "unparse") else str(node.returns)
    )
    return "dict[" in annotation_str


def check_file(file_path: Path) -> List[str]:
    """Check a file for functions with dict return annotations."""
    errors = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content, filename=str(file_path))
    except SyntaxError:
        return [f"{file_path}:1:1: E999 SyntaxError in file"]

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if has_dict_return_annotation(node):
                errors.append(
                    f"{file_path}:{node.lineno}:1: Function '{node.name}' returns dict type instead of pydantic model"
                )

    return errors


def main() -> int:
    """Main entry point."""
    src_dir = Path("src")
    if not src_dir.exists():
        import sys

        print("Error: src/ directory not found", file=sys.stderr)
        return 1

    all_errors = []
    for py_file in src_dir.rglob("*.py"):
        if "tests" in py_file.parts:
            continue
        errors = check_file(py_file)
        all_errors.extend(errors)

    for error in all_errors:
        print(error)

    return 1 if all_errors else 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
