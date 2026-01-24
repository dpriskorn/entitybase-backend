#!/usr/bin/env python3
"""Linter to check if all public classes inherit from BaseModel."""

import ast
from pathlib import Path
from typing import List


def is_basemodel_subclass(node: ast.ClassDef) -> bool:
    """Check if a class inherits from BaseModel or should be considered a model."""
    for base in node.bases:
        if isinstance(base, ast.Name):
            if base.id in ("BaseModel", "Value"):
                return True
            # Skip enums, protocols, and other non-Pydantic classes
            if base.id in (
                "Enum",
                "object",
                "Protocol",
                # "BaseSettings",
                # "Client",
                # "ConnectionManager",
                # "EntityTransaction",
                # "TripleWriters",
            ):
                return True
        elif isinstance(base, ast.Attribute) and base.attr == "BaseModel":
            return True
        elif isinstance(base, ast.Attribute) and base.attr in (
            "BaseSettings",
            "Protocol",
            "Value",
            "Client",
            "ConnectionManager",
            "EntityTransaction",
        ):
            return True
    return False


def has_attributes(node: ast.ClassDef) -> bool:
    """Check if a class has any attributes (assignments or annotations)."""
    for stmt in node.body:
        if isinstance(stmt, (ast.Assign, ast.AnnAssign)):
            return True
    return False


def check_file(file_path: Path) -> List[str]:
    """Check a file for classes not inheriting from BaseModel."""
    errors = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content, filename=str(file_path))
    except SyntaxError:
        return [f"{file_path}:1:1: E999 SyntaxError in file"]

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if (
                not node.name.startswith("_")
                and node.name != "TripleWriters"
                and not is_basemodel_subclass(node)
                and has_attributes(node)
            ):
                errors.append(
                    f"{file_path}:{node.lineno}:1: Class '{node.name}' does not inherit from BaseModel"
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
