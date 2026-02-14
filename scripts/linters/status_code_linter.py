#!/usr/bin/env python3
"""
Linter to check for multiple status_codes in test asserts.

Detects patterns like:
- assert response.status_code in [200, 201]
- assert response.status_code == 200 or response.status_code == 201
- Multiple separate status_code asserts in the same test function
"""

import ast
import sys
from pathlib import Path
from typing import List, Set, Tuple

sys.path.append(str(Path(__file__).parent.resolve()))

from allowlist_utils import is_line_allowed


class StatusCodeAssertChecker(ast.NodeVisitor):
    """AST visitor to check for multiple status_code patterns in asserts."""

    def __init__(self, source_lines: List[str], file_path: str, allowlist: Set[str]):
        self.source_lines = source_lines
        self.file_path = file_path
        self.allowlist = allowlist
        self.violations: List[Tuple[str, int, str, str]] = []
        self.current_function: str = ""
        self.function_status_asserts: dict[str, List[int]] = {}

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        old_function = self.current_function
        self.current_function = node.name
        if node.name.startswith("test_"):
            self.function_status_asserts[node.name] = []
        self.generic_visit(node)
        self.current_function = old_function

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        old_function = self.current_function
        self.current_function = node.name
        if node.name.startswith("test_"):
            self.function_status_asserts[node.name] = []
        self.generic_visit(node)
        self.current_function = old_function

    def visit_Assert(self, node: ast.Assert) -> None:
        self._check_assert(node)
        self.generic_visit(node)

    def _check_assert(self, node: ast.Assert) -> None:
        if not self.current_function.startswith("test_"):
            return

        if self._has_in_list_pattern(node.test):
            if is_line_allowed(self.file_path, node.lineno, self.allowlist):
                return
            self.violations.append(
                (
                    self.current_function,
                    node.lineno,
                    "assert with 'status_code in [...]' pattern - use a single expected status",
                    str(self.file_path),
                )
            )
            return

        if self._has_or_pattern(node.test):
            if is_line_allowed(self.file_path, node.lineno, self.allowlist):
                return
            self.violations.append(
                (
                    self.current_function,
                    node.lineno,
                    "assert with 'status_code == X or status_code == Y' pattern - use a single expected status",
                    str(self.file_path),
                )
            )
            return

        if self._contains_status_code_check(node.test):
            if self.current_function in self.function_status_asserts:
                self.function_status_asserts[self.current_function].append(node.lineno)

    def _has_in_list_pattern(self, node: ast.AST) -> bool:
        if isinstance(node, ast.Compare):
            for i, op in enumerate(node.ops):
                if isinstance(op, ast.In):
                    comparator = node.comparators[i]
                    if isinstance(comparator, ast.List):
                        if self._contains_status_code_reference(node.left):
                            return True
                        for elt in comparator.elts:
                            if isinstance(elt, ast.Constant) and isinstance(
                                elt.value, int
                            ):
                                if 100 <= elt.value <= 599:
                                    if self._contains_status_code_reference(node.left):
                                        return True
        return False

    def _has_or_pattern(self, node: ast.AST) -> bool:
        if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
            status_checks = 0
            for value in node.values:
                if self._is_status_code_comparison(value):
                    status_checks += 1
            return status_checks >= 2
        return False

    def _is_status_code_comparison(self, node: ast.AST) -> bool:
        if isinstance(node, ast.Compare):
            if self._contains_status_code_reference(node.left):
                for comparator in node.comparators:
                    if isinstance(comparator, ast.Constant) and isinstance(
                        comparator.value, int
                    ):
                        if 100 <= comparator.value <= 599:
                            return True
        return False

    def _contains_status_code_check(self, node: ast.AST) -> bool:
        return self._contains_status_code_reference(node)

    def _contains_status_code_reference(self, node: ast.AST) -> bool:
        if isinstance(node, ast.Attribute):
            if node.attr == "status_code":
                return True
            return self._contains_status_code_reference(node.value)
        if isinstance(node, ast.Compare):
            if self._contains_status_code_reference(node.left):
                return True
            for comp in node.comparators:
                if self._contains_status_code_reference(comp):
                    return True
        if isinstance(node, ast.BoolOp):
            for value in node.values:
                if self._contains_status_code_reference(value):
                    return True
        if isinstance(node, ast.Call):
            if self._contains_status_code_reference(node.func):
                return True
            for arg in node.args:
                if self._contains_status_code_reference(arg):
                    return True
        return False

    def get_multiple_assert_violations(self) -> List[Tuple[str, int, str, str]]:
        violations = []
        for func_name, line_numbers in self.function_status_asserts.items():
            if len(line_numbers) >= 3:
                for line_no in line_numbers:
                    if is_line_allowed(self.file_path, line_no, self.allowlist):
                        continue
                    violations.append(
                        (
                            func_name,
                            line_no,
                            f"test function '{func_name}' has {len(line_numbers)} status_code asserts - consider splitting into separate tests",
                            str(self.file_path),
                        )
                    )
        return violations


def check_file(file_path: Path, allowlist: Set[str]) -> List[Tuple[str, int, str, str]]:
    """Check a single Python file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()

        source_lines = source.splitlines()
        tree = ast.parse(source, filename=str(file_path))

        checker = StatusCodeAssertChecker(source_lines, str(file_path), allowlist)
        checker.visit(tree)

        violations = checker.violations
        violations.extend(checker.get_multiple_assert_violations())

        return violations

    except SyntaxError:
        return [(str(file_path), 0, f"Syntax error in {file_path}", str(file_path))]
    except Exception as e:
        return [
            (str(file_path), 0, f"Error processing {file_path}: {e}", str(file_path))
        ]


def load_allowlist() -> Set[str]:
    """Load the allowlist from config/linters/allowlists/custom/status-code.txt."""
    allowlist_path = Path("config/linters/allowlists/custom/status-code.txt")
    allowlist: Set[str] = set()
    if allowlist_path.exists():
        with open(allowlist_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    allowlist.add(line)
    return allowlist


def main() -> None:
    """Main entry point."""
    tests_dir = Path("tests")
    if not tests_dir.exists():
        print("No tests/ directory found")
        return

    allowlist = load_allowlist()

    violations = []

    for py_file in tests_dir.rglob("*.py"):
        if py_file.name.startswith("test_"):
            violations.extend(check_file(py_file, allowlist))

    if violations:
        print("Status code assert violations:")
        allowlist_entries = []
        seen = set()
        for func_name, line_no, message, file_path in violations:
            key = (file_path, line_no, message)
            if key not in seen:
                seen.add(key)
                print(f"{file_path}:{line_no}: {message}")
                allowlist_entries.append(f"{file_path}:{line_no}")
        allowlist_path = Path("config/linters/allowlists/custom/status-code.txt")
        print(f"\nTo allowlist violations, add these entries to {allowlist_path}:")
        for entry in allowlist_entries:
            print(entry)
        sys.exit(1)
    else:
        print("No status code assert violations found")


if __name__ == "__main__":
    main()
