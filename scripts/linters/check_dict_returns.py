#!/usr/bin/env python3
"""
Linter to check for functions returning -> dict instead of proper models.
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple

# List of functions allowed to return dict types
ALLOWED_DICT_RETURNS = [
    "get_batch_sitelinks",
    "get_batch_labels",
    "get_batch_descriptions",
    "get_batch_aliases",
    "get_batch_statements",
    "load_metadata",
    "batch_get_statements",
    "data",
    "get_entity_json_revision",
    "get_openapi",
]


class DictReturnChecker(ast.NodeVisitor):
    """AST visitor to check for -> dict return annotations."""

    def __init__(self, source_lines: List[str]):
        self.source_lines = source_lines
        self.violations: List[Tuple[str, int, str]] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_function(node)
        self.generic_visit(node)

    def _check_function(self, node) -> None:
        if node.returns:
            return_annotation = self._get_annotation_string(node.returns)
            if self._is_dict_annotation(return_annotation):
                func_name = node.name
                if func_name not in ALLOWED_DICT_RETURNS:
                    self.violations.append(
                        (
                            func_name,
                            node.lineno,
                            f"Function '{func_name}' returns -> {return_annotation}, consider using a proper Pydantic model",
                        )
                    )

    # noinspection PyUnresolvedReferences
    def _get_annotation_string(self, node: ast.AST) -> str:
        """Convert AST annotation to string."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Subscript):
            if isinstance(node.value, ast.Name):
                base = node.value.id
                if isinstance(node.slice, ast.Index):  # Python < 3.9
                    return f"{base}[{self._get_annotation_string(node.slice.value)}]"
                else:
                    return f"{base}[{self._get_annotation_string(node.slice)}]"
        return ast.unparse(node) if hasattr(ast, "unparse") else str(node)

    def _is_dict_annotation(self, annotation: str) -> bool:
        """Check if annotation is a dict type."""
        return "dict" in annotation.lower()


def check_file(file_path: Path) -> List[Tuple[str, int, str]]:
    """Check a single Python file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()

        source_lines = source.splitlines()
        tree = ast.parse(source, filename=str(file_path))

        checker = DictReturnChecker(source_lines)
        checker.visit(tree)

        return checker.violations

    except SyntaxError:
        return [(str(file_path), 0, f"Syntax error in {file_path}")]
    except Exception as e:
        return [(str(file_path), 0, f"Error processing {file_path}: {e}")]


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python check_dict_returns.py <path>")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Path {path} does not exist")
        sys.exit(1)

    violations = []

    if path.is_file() and path.suffix == ".py":
        violations.extend(check_file(path))
    elif path.is_dir():
        for py_file in path.rglob("*.py"):
            # Skip test files and certain directories
            if "test" in py_file.parts or "tests" in py_file.parts:
                continue
            if py_file.name.startswith("test_"):
                continue
            if "workers" in py_file.parts or "scripts" in py_file.parts:
                continue
            violations.extend(check_file(py_file))

    if violations:
        print("Dict return violations:")
        for func_name, line_no, message in violations:
            print(f"{message} at line {line_no}")
        sys.exit(1)
    else:
        print("No dict return violations found")


if __name__ == "__main__":
    main()
