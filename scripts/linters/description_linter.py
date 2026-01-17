#!/usr/bin/env python3
"""
Linter to check that Pydantic model fields in API response models have descriptions.
"""

import ast
import sys
from pathlib import Path


def check_descriptions(models_dir: Path) -> list[str]:
    violations = []
    for file in sorted(models_dir.rglob("*.py")):
        try:
            tree = ast.parse(file.read_text(), filename=str(file))
            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.ClassDef)
                    and any(
                        (isinstance(base, ast.Name) and base.id == "BaseModel")
                        or (isinstance(base, ast.Attribute) and base.attr == "BaseModel")
                        for base in node.bases
                    )
                ):
                    for item in node.body:
                        if (
                            isinstance(item, ast.AnnAssign)
                            and isinstance(item.target, ast.Name)
                            and item.target.id
                            and not item.target.id.startswith("_")
                        ):
                            field_name = item.target.id
                            has_description = False
                            if (
                                item.value
                                and isinstance(item.value, ast.Call)
                                and isinstance(item.value.func, ast.Name)
                                and item.value.func.id == "Field"
                                and item.value.keywords
                            ):
                                for kw in item.value.keywords:
                                    if kw.arg == "description":
                                        has_description = True
                                        break
                            if not has_description:
                                violations.append(
                                    f"Field '{field_name}' in {node.name} ({file.relative_to(models_dir.parent.parent)}) lacks a description"
                                )
        except SyntaxError as e:
            violations.append(f"Syntax error in {file}: {e}")
    return violations


def main():
    if len(sys.argv) != 2:
        print("Usage: python description_linter.py <models_dir>")
        sys.exit(1)

    models_dir = Path(sys.argv[1])
    if not models_dir.exists():
        print(f"Directory {models_dir} does not exist")
        sys.exit(1)

    violations = check_descriptions(models_dir)
    if violations:
        for violation in violations:
            print(violation)
        sys.exit(1)
    else:
        print("All fields have descriptions.")


if __name__ == "__main__":
    main()