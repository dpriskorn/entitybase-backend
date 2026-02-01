#!/usr/bin/env python3
"""
Linter to check for functions returning -> dict instead of proper models.
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple


class DictReturnChecker(ast.NodeVisitor):
    """AST visitor to check for -> dict return annotations."""

    def __init__(self, source_lines: List[str], file_path: str, allowlist: set):
        self.source_lines = source_lines
        self.file_path = file_path
        self.allowlist = allowlist
        self.violations: List[Tuple[str, int, str, str]] = []

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
                key = f"{self.file_path}:{node.lineno}"
                if key not in self.allowlist:
                    func_name = node.name
                    self.violations.append(
                        (
                            func_name,
                            node.lineno,
                            f"Function '{func_name}' returns -> {return_annotation}, consider using a proper Pydantic model",
                            str(self.file_path),
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
                try:
                    slice_str = self._get_annotation_string(node.slice)
                    return f"{base}[{slice_str}]"
                except (AttributeError, TypeError):
                    pass
        return ast.unparse(node) if hasattr(ast, "unparse") else str(node)

    @staticmethod
    def _is_dict_annotation(annotation: str) -> bool:
        """Check if annotation is a dict type."""
        return "dict" in annotation.lower()


def check_file(file_path: Path, allowlist: set) -> List[Tuple[str, int, str, str]]:
    """Check a single Python file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()

        source_lines = source.splitlines()
        tree = ast.parse(source, filename=str(file_path))

        checker = DictReturnChecker(source_lines, str(file_path), allowlist)
        checker.visit(tree)

        return checker.violations

    except SyntaxError:
        return [(str(file_path), 0, f"Syntax error in {file_path}", str(file_path))]
    except Exception as e:
        return [(str(file_path), 0, f"Error processing {file_path}: {e}", str(file_path))]


def load_allowlist() -> set:
    """Load the allowlist from config/linters/allowlists/custom/dict.txt."""
    allowlist_path = Path("config/linters/allowlists/custom/dict.txt")
    allowlist = set()
    if allowlist_path.exists():
        with open(allowlist_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    allowlist.add(line)
    return allowlist


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python check_dict_returns.py <path>")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Path {path} does not exist")
        sys.exit(1)

    allowlist = load_allowlist()

    violations = []

    if path.is_file() and path.suffix == ".py":
        violations.extend(check_file(path, allowlist))
    elif path.is_dir():
        for py_file in path.rglob("*.py"):
            # Skip test files and certain directories
            if "test" in py_file.parts or "tests" in py_file.parts:
                continue
            if py_file.name.startswith("test_"):
                continue
            if "workers" in py_file.parts or "scripts" in py_file.parts:
                continue
            violations.extend(check_file(py_file, allowlist))

    if violations:
        print("Dict return violations:")
        allowlist_entries = []
        for func_name, line_no, message, file_path in violations:
            print(f"{file_path}:{line_no}: {message}")
            allowlist_entries.append(f"{file_path}:{line_no}")
        allowlist_path = Path("config/linters/allowlists/custom/dict.txt")
        print(f"\nTo allowlist violations, add these entries to {allowlist_path}:")
        for entry in allowlist_entries:
            print(entry)
        sys.exit(1)
    else:
        print("No dict return violations found")


if __name__ == "__main__":
    main()
