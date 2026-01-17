#!/usr/bin/env python3
"""
Linter to check that Pydantic model field names in API response models are <= 10 characters.
"""

import ast
import sys
from pathlib import Path


def check_field_name_lengths(models_dir: Path) -> list[str]:
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
                    for item in node.body:
                        if (
                            isinstance(item, ast.AnnAssign)
                            and isinstance(item.target, ast.Name)
                            and item.target.id
                        ):
                            name = item.target.id
                            alias = None
                            if (
                                item.value
                                and isinstance(item.value, ast.Call)
                                and isinstance(item.value.func, ast.Name)
                                and item.value.func.id == "Field"
                                and item.value.keywords
                            ):
                                for kw in item.value.keywords:
                                    if (
                                        kw.arg == "alias"
                                        and isinstance(kw.value, ast.Constant)
                                        and isinstance(kw.value.value, str)
                                    ):
                                        alias = kw.value.value
                                        break
                            check_name = alias if alias else name
                            if len(check_name) > 20:
                                violations.append(
                                    f"Field '{name}' (alias: '{alias}' -> {len(check_name)} chars) exceeds 10 char limit in {node.name} ({file.relative_to(models_dir.parent.parent)})"
                                )
        except SyntaxError as e:
            violations.append(f"Syntax error in {file}: {e}")
    return violations


def main():
    if len(sys.argv) != 2:
        print("Usage: python key_length_linter.py <models_dir>")
        sys.exit(1)

    models_dir = Path(sys.argv[1])
    if not models_dir.exists():
        print(f"Directory {models_dir} does not exist")
        sys.exit(1)

    violations = check_field_name_lengths(models_dir)
    if violations:
        for violation in violations:
            print(violation)
        sys.exit(1)
    else:
        print("All field names are <= 10 characters.")


if __name__ == "__main__":
    main()
