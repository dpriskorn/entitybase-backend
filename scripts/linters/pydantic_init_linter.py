#!/usr/bin/env python3
"""Linter to check for __init__ methods in Pydantic BaseModel subclasses, suggesting model_post_init instead."""

import ast
import sys
from pathlib import Path
from typing import List, Set

sys.path.append(str(Path(__file__).parent.resolve()))

from allowlist_utils import is_line_allowed


PYDANTIC_BASES = {"pydantic.BaseModel", "pydantic.main.BaseModel"}
PROJECT_BASE = "models.base.Base"


def collect_imports(tree: ast.AST) -> dict[str, str]:
    """Collect import aliases to resolve base class names."""
    imports: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module:
                for alias in node.names:
                    full_name = f"{node.module}.{alias.name}"
                    imports[alias.asname or alias.name] = full_name
                    imports[alias.name] = full_name
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports[alias.asname or alias.name] = alias.name
    return imports


def resolve_base_name(base: ast.expr, imports: dict[str, str]) -> str | None:
    """Resolve base class name to full dotted path."""
    if isinstance(base, ast.Name):
        return imports.get(base.id, base.id)
    elif isinstance(base, ast.Attribute):
        if isinstance(base.value, ast.Name):
            module = imports.get(base.value.id, base.value.id)
            return f"{module}.{base.attr}"
    return None


def get_class_bases_recursive(
    base: ast.expr, imports: dict[str, str], tree: ast.AST, visited: Set[str] | None = None
) -> List[str]:
    """Recursively resolve class bases to find all ancestor fully-qualified names."""
    if visited is None:
        visited = set()

    resolved = []
    base_name = resolve_base_name(base, imports)
    if not base_name:
        return resolved

    if base_name in visited:
        return resolved
    visited.add(base_name)
    resolved.append(base_name)

    if base_name in PYDANTIC_BASES:
        return resolved

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_base_name = resolve_base_name(node.name, imports)
            if class_base_name == base_name or node.name == base_name:
                for inner_base in node.bases:
                    inner_bases = get_class_bases_recursive(inner_base, imports, tree, visited)
                    resolved.extend(inner_bases)

    return resolved


def check_file(file_path: Path, allowlist: set) -> List[str]:
    """Check a file for __init__ methods in classes."""
    errors = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content, filename=str(file_path))
    except SyntaxError:
        return [f"{file_path}:1:1: E999 SyntaxError in file"]

    imports = collect_imports(tree)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "__init__":
            if is_line_allowed(str(file_path), node.lineno, allowlist):
                continue

            class_name = None
            class_bases: List[ast.expr] = []
            for parent in ast.walk(tree):
                if isinstance(parent, ast.ClassDef) and node in parent.body:
                    class_name = parent.name
                    class_bases = parent.bases
                    break

            if not class_name:
                continue

            all_bases: List[str] = []
            for base in class_bases:
                resolved_bases = get_class_bases_recursive(base, imports, tree)
                all_bases.extend(resolved_bases)

            has_project_base = PROJECT_BASE in all_bases
            has_pydantic_base = bool(set(all_bases) & PYDANTIC_BASES)

            if has_project_base:
                continue

            if has_pydantic_base:
                errors.append(
                    f"{file_path}:{node.lineno}:1: Class '{class_name}' defines __init__. "
                    f"Consider using model_post_init if it's a Pydantic model. "
                    f"(add to allowlist: {file_path}:{node.lineno})"
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
    sys.exit(main())
