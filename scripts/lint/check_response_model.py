#!/usr/bin/env python3
"""Linter to check for response_model=dict in FastAPI endpoints."""

import ast
import sys
from pathlib import Path


def check_response_model_dict(file_path: Path) -> list[str]:
    """Check if file has response_model=dict in FastAPI decorators."""
    errors = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content, filename=str(file_path))

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        # Check if decorator is app.get, app.post, etc.
                        if isinstance(decorator.func, ast.Attribute):
                            if decorator.func.attr in [
                                "get",
                                "post",
                                "put",
                                "delete",
                                "patch",
                            ]:
                                for keyword in decorator.keywords:
                                    if keyword.arg == "response_model":
                                        if (
                                            isinstance(keyword.value, ast.Name)
                                            and keyword.value.id == "dict"
                                        ):
                                            errors.append(
                                                f"{file_path}:{decorator.lineno}: "
                                                f"Endpoint '{node.name}' has response_model=dict, "
                                                f"use a proper Pydantic model instead"
                                            )
    except Exception as e:
        errors.append(f"Error parsing {file_path}: {e}")

    return errors


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python check_response_model.py <directory>")
        sys.exit(1)

    directory = Path(sys.argv[1])
    if not directory.is_dir():
        print(f"{directory} is not a directory")
        sys.exit(1)

    errors = []
    for py_file in directory.rglob("*.py"):
        errors.extend(check_response_model_dict(py_file))

    if errors:
        for error in errors:
            print(error)
        sys.exit(1)
    else:
        print("No response_model=dict found")


if __name__ == "__main__":
    main()
