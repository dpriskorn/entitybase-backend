#!/usr/bin/env python3
"""
Custom linter to check that methods with more than 30 lines contain at least one logger call (info, debug, warning, error, critical).

Tiered requirements based on function size:
- 31-50 lines: at least 1 logger call
- 51-80 lines: at least 2 logger calls
- 81+ lines: at least 3 logger calls
"""

import ast
import sys
from pathlib import Path
from typing import List
from pydantic import BaseModel

sys.path.append(str(Path(__file__).parent.resolve()))

# noinspection PyUnresolvedReferences
from allowlist_utils import is_line_allowed

# Tiered logger requirements based on function size (max_lines, min_calls)
LOGGER_TIERS = [
    (50, 1),  # 31-50 lines: at least 1 logger call
    (80, 2),  # 51-80 lines: at least 2 logger calls
    (float("inf"), 3),  # 81+ lines: at least 3 logger calls
]

MIN_LINES_THRESHOLD = 30  # Only check functions with more than this many lines


class LoggerViolation(BaseModel):
    """Represents a logger violation found during linting."""

    func_name: str
    line_no: int
    message: str
    file_path: str


def load_allowlist() -> set:
    """Load the logger allowlist from config/linters/allowlists/logger.txt."""
    allowlist_path = Path("config/linters/allowlists/logger.txt")
    allowlist = set()
    if allowlist_path.exists():
        with open(allowlist_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    allowlist.add(line)
    return allowlist


class LoggerInfoChecker(ast.NodeVisitor):
    """AST visitor to check logger.info() calls in functions."""

    def __init__(self, source_lines: List[str], file_path: str, allowlist: set):
        self.source_lines = source_lines
        self.file_path = file_path
        self.allowlist = allowlist
        self.violations: List[LoggerViolation] = []
        self.current_class = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        old_class = self.current_class
        self.current_class = node
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_function(node)
        self.generic_visit(node)

    def _check_function(self, node) -> None:
        # Skip functions in Enum classes
        if self.current_class and self._is_enum_class(self.current_class):
            return

        # Skip abstract methods
        if self._is_abstract_method(node):
            return

        # Calculate function line count
        start_line = node.lineno - 1  # 0-based
        end_line = (
            node.end_lineno - 1 if node.end_lineno else len(self.source_lines) - 1
        )

        # Count non-empty lines in function body
        body_lines = 0
        for i in range(start_line, end_line + 1):
            line = self.source_lines[i].strip()
            if line and not line.startswith("#"):
                body_lines += 1

        if body_lines <= MIN_LINES_THRESHOLD:
            return

        # Get required logger count based on function size
        required_count = self._get_required_logger_count(body_lines)

        # Count logger calls
        logger_call_count = 0
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if self._is_logger_call(child):
                    logger_call_count += 1

        if logger_call_count < required_count:
            func_name = node.name
            if is_line_allowed(self.file_path, node.lineno, self.allowlist):
                return
            self.violations.append(
                LoggerViolation(
                    func_name=func_name,
                    line_no=node.lineno,
                    message=f"Function '{func_name}' has {body_lines} lines and {logger_call_count} logger call(s) but needs at least {required_count}",
                    file_path=self.file_path,
                )
            )

    @staticmethod
    def _get_required_logger_count(body_lines: int) -> int:
        """Get minimum number of logger calls required based on function size."""
        for max_lines, min_calls in LOGGER_TIERS:
            if body_lines <= max_lines:
                return min_calls
        return 3  # Fallback for very large functions

        # Count non-empty lines in function body
        body_lines = 0
        for i in range(start_line, end_line + 1):
            line = self.source_lines[i].strip()
            if line and not line.startswith("#"):
                body_lines += 1

        if body_lines <= 30:
            return

        # Check for logger calls
        has_logger_call = False
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if self._is_logger_call(child):
                    has_logger_call = True
                    break

        if not has_logger_call:
            func_name = node.name
            if is_line_allowed(self.file_path, node.lineno, self.allowlist):
                return
            self.violations.append(
                LoggerViolation(
                    func_name=func_name,
                    line_no=node.lineno,
                    message=f"Function '{func_name}' has {body_lines} lines but no logger.debug() call",
                    file_path=self.file_path,
                )
            )

    def _is_logger_call(self, node: ast.Call) -> bool:
        """Check if this is a logger call (info, debug, warning, error, critical)."""
        if isinstance(node.func, ast.Attribute):
            if self._is_logger_expr(node.func.value):
                if node.func.attr in ["info", "debug", "warning", "error", "critical"]:
                    return True
        return False

    def _is_logger_expr(self, node) -> bool:
        """Check if the expression refers to logger or log."""
        if isinstance(node, ast.Name):
            return hasattr(node, "id") and node.id in ["logger", "log"]
        if isinstance(node, ast.Attribute):
            return node.attr in ["logger", "log"] or self._is_logger_expr(node.value)
        return False

    @staticmethod
    def _is_enum_class(node: ast.ClassDef) -> bool:
        """Check if class inherits from Enum."""
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == "Enum":
                return True
            elif isinstance(base, ast.Attribute) and base.attr == "Enum":
                return True
        return False

    @staticmethod
    def _is_abstract_method(node) -> bool:
        """Check if function is decorated with @abstractmethod."""
        if hasattr(node, "decorator_list"):
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name) and decorator.id == "abstractmethod":
                    return True
                elif (
                    isinstance(decorator, ast.Attribute)
                    and decorator.attr == "abstractmethod"
                ):
                    return True
        return False


def check_file(file_path: Path, allowlist: set) -> List[LoggerViolation]:
    """Check a single Python file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()

        source_lines = source.splitlines()
        tree = ast.parse(source, filename=str(file_path))

        checker = LoggerInfoChecker(source_lines, str(file_path), allowlist)
        checker.visit(tree)

        return checker.violations

    except SyntaxError:
        return [
            LoggerViolation(
                func_name="",
                line_no=0,
                message=f"Syntax error in {file_path}",
                file_path=str(file_path),
            )
        ]
    except Exception as e:
        return [
            LoggerViolation(
                func_name="",
                line_no=0,
                message=f"Error processing {file_path}: {e}",
                file_path=str(file_path),
            )
        ]


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python check_logger_info.py <path>")
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
        print("Logger check violations:")
        for violation in violations:
            print(
                f"{violation.message} at line {violation.line_no}: {violation.file_path}"
            )
        allowlist_path = Path("config/linters/allowlists/logger.txt")
        print(f"To allowlist violations, add 'file:line' entries to {allowlist_path}")
        sys.exit(1)
    else:
        print("All functions pass logger check")


if __name__ == "__main__":
    main()
