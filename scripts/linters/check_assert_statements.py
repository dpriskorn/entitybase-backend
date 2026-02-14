#!/usr/bin/env python3
"""Linter to check for assert statements that should use raise_validation_error()."""

import ast
import sys
from pathlib import Path
from typing import List, Tuple

sys.path.append(str(Path(__file__).parent.resolve()))

from allowlist_utils import is_line_allowed


EXCLUDED_FILES: set[str] = set()


class AssertChecker(ast.NodeVisitor):
    """AST visitor to check for assert statements."""

    def __init__(self, file_path: str, allowlist: set[str]):
        self.file_path = file_path
        self.allowlist = allowlist
        self.violations: List[Tuple[str, int, str, str]] = []

    def visit_Assert(self, node: ast.Assert) -> None:
        if is_line_allowed(self.file_path, node.lineno, self.allowlist):
            return
        self.violations.append(
            (
                "",
                node.lineno,
                "Found assert statement - use raise_validation_error(...) instead",
                str(self.file_path),
            )
        )
        self.generic_visit(node)


def check_file(file_path: Path, allowlist: set[str]) -> List[Tuple[str, int, str, str]]:
    """Check a single Python file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source, filename=str(file_path))
        checker = AssertChecker(str(file_path), allowlist)
        checker.visit(tree)
        return checker.violations
    except SyntaxError:
        return [(str(file_path), 0, f"Syntax error in {file_path}", str(file_path))]
    except Exception as e:
        return [
            (str(file_path), 0, f"Error processing {file_path}: {e}", str(file_path))
        ]


def load_allowlist() -> set[str]:
    """Load the allowlist from config/linters/allowlists/custom/assert_statements.txt."""
    allowlist_path = Path("config/linters/allowlists/custom/assert_statements.txt")
    if not allowlist_path.exists():
        return set()
    with open(allowlist_path, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip() and not line.startswith("#")}


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python check_assert_statements.py <path>")
        return 1

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Path {path} does not exist")
        return 1

    allowlist = load_allowlist()
    violations = []

    if path.is_file() and path.suffix == ".py":
        violations.extend(check_file(path, allowlist))
    elif path.is_dir():
        for py_file in path.rglob("*.py"):
            if "tests" in py_file.parts or "scripts" in py_file.parts:
                continue
            if py_file.name.startswith("test_"):
                continue
            violations.extend(check_file(py_file, allowlist))

    if violations:
        for _, line_no, message, file_path in violations:
            print(f"{file_path}:{line_no}:1: {message}")
        return 1

    print("No assert statement violations found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
