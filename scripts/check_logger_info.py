#!/usr/bin/env python3
"""
Custom linter to check that methods with more than 20 lines contain at least one logger.info() call.
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple


class LoggerInfoChecker(ast.NodeVisitor):
    """AST visitor to check logger.info() calls in functions."""

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
        # Calculate function line count
        start_line = node.lineno - 1  # 0-based
        end_line = node.end_lineno - 1 if node.end_lineno else len(self.source_lines) - 1

        # Count non-empty lines in function body
        body_lines = 0
        for i in range(start_line, end_line + 1):
            line = self.source_lines[i].strip()
            if line and not line.startswith('#'):
                body_lines += 1

        if body_lines <= 20:
            return

        # Check for logger.info() calls
        has_logger_info = False
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if self._is_logger_info_call(child):
                    has_logger_info = True
                    break

        if not has_logger_info:
            func_name = node.name
            self.violations.append((
                func_name,
                node.lineno,
                f"Function '{func_name}' has {body_lines} lines but no logger.info() call"
            ))

    def _is_logger_info_call(self, node: ast.Call) -> bool:
        """Check if this is a logger.info() call."""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id in ['logger', 'log']:
                if node.func.attr == 'info':
                    return True
        return False


def check_file(file_path: Path) -> List[Tuple[str, int, str]]:
    """Check a single Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()

        source_lines = source.splitlines()
        tree = ast.parse(source, filename=str(file_path))

        checker = LoggerInfoChecker(source_lines)
        checker.visit(tree)

        return checker.violations

    except SyntaxError:
        return [(str(file_path), 0, f"Syntax error in {file_path}")]
    except Exception as e:
        return [(str(file_path), 0, f"Error processing {file_path}: {e}")]


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python check_logger_info.py <path>")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Path {path} does not exist")
        sys.exit(1)

    violations = []

    if path.is_file() and path.suffix == '.py':
        violations.extend(check_file(path))
    elif path.is_dir():
        for py_file in path.rglob('*.py'):
            # Skip test files and certain directories
            if 'test' in py_file.parts or 'tests' in py_file.parts:
                continue
            if py_file.name.startswith('test_'):
                continue
            violations.extend(check_file(py_file))

    if violations:
        print("Logger info check violations:")
        for func_name, line_no, message in violations:
            print(f"{message} at line {line_no}")
        sys.exit(1)
    else:
        print("All functions pass logger info check")


if __name__ == '__main__':
    main()