#!/usr/bin/env python3
"""
Linter to check that Pydantic BaseModel classes in API response models have docstrings.
"""

import ast
import sys
from pathlib import Path


def check_docstrings(models_dir: Path) -> list[str]:
    violations = []
    for file in sorted(models_dir.rglob("*.py")):
        try:
            tree = ast.parse(file.read_text(), filename=str(file))
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and any(
                    (isinstance(base, ast.Name) and base.id == "BaseModel")
                    or (isinstance(base, ast.Attribute) and base.attr == "BaseModel")
                    for base in node.bases
                ):
                    # Check if the class has a docstring
                    has_docstring = (
                        node.body
                        and isinstance(node.body[0], ast.Expr)
                        and isinstance(node.body[0].value, ast.Constant)
                        and isinstance(node.body[0].value.value, str)
                    )
                    if not has_docstring:
                        violations.append(
                            f"Class '{node.name}' in {file.relative_to(models_dir.parent.parent)} lacks a docstring"
                        )
        except SyntaxError as e:
            violations.append(f"Syntax error in {file}: {e}")
    return violations


def main():
    if len(sys.argv) != 2:
        print("Usage: python docstring_linter.py <models_dir>")
        sys.exit(1)

    models_dir = Path(sys.argv[1])
    if not models_dir.exists():
        print(f"Directory {models_dir} does not exist")
        sys.exit(1)

    violations = check_docstrings(models_dir)
    if violations:
        for violation in violations:
            print(violation)
        sys.exit(1)
    else:
        print("All BaseModel classes have docstrings.")


if __name__ == "__main__":
    main()
