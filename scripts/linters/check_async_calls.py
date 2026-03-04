#!/usr/bin/env python3
#!/usr/bin/env python3
"""Linter to detect async method calls without await in entity handlers.

This linter specifically checks for known async methods in entity transaction handlers
that MUST be awaited. It targets:
- publish_event calls on transaction objects (ctx.tx, tx)
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple

sys.path.append(str(Path(__file__).parent.resolve()))

from allowlist_utils import is_line_allowed

EXCLUDED_FILES: set[str] = set()


class ParentSetter(ast.NodeVisitor):
    """AST visitor to set parent references."""

    def __init__(self):
        self.parent = None

    def generic_visit(self, node):
        for child in ast.iter_child_nodes(node):
            child.parent = node
            self.generic_visit(child)


class AsyncCallChecker(ast.NodeVisitor):
    """AST visitor to detect async calls without await."""

    def __init__(self, file_path: str, allowlist: set[str]):
        self.file_path = file_path
        self.allowlist = allowlist
        self.violations: List[Tuple[str, int, str, str]] = []

    def visit_Call(self, node: ast.Call) -> None:
        if is_line_allowed(self.file_path, node.lineno, self.allowlist):
            self.generic_visit(node)
            return

        if not self._is_awaited(node):
            if self._is_tx_publish_event_call(node):
                self.violations.append(
                    (
                        self.file_path,
                        node.lineno,
                        "Async method 'publish_event' called without await on transaction object",
                        self.file_path,
                    )
                )

        self.generic_visit(node)

    def _is_awaited(self, node: ast.AST) -> bool:
        """Check if node is inside an Await expression by walking up parents."""
        parent = getattr(node, "parent", None)
        while parent:
            if isinstance(parent, ast.Await):
                return True
            parent = getattr(parent, "parent", None)
        return False

    def _is_tx_publish_event_call(self, node: ast.Call) -> bool:
        """Check if this is a tx.publish_event() or ctx.tx.publish_event() call."""
        if not isinstance(node.func, ast.Attribute):
            return False

        if node.func.attr != "publish_event":
            return False

        if isinstance(node.func.value, ast.Attribute):
            if node.func.value.attr == "tx":
                return True
        elif isinstance(node.func.value, ast.Name):
            if node.func.value.id in ("tx", "transaction"):
                return True

        return False


def check_file(file_path: Path, allowlist: set[str]) -> List[Tuple[str, int, str, str]]:
    """Check a single Python file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source, filename=str(file_path))
        ParentSetter().visit(tree)
        checker = AsyncCallChecker(str(file_path), allowlist)
        checker.visit(tree)
        return checker.violations
    except SyntaxError:
        return [(str(file_path), 0, f"Syntax error in {file_path}", str(file_path))]


def load_allowlist() -> set[str]:
    """Load the allowlist from config/linters/allowlists/custom/check_async_calls.txt."""
    allowlist_path = Path("config/linters/allowlists/custom/check_async_calls.txt")
    if not allowlist_path.exists():
        return set()
    with open(allowlist_path, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip() and not line.startswith("#")}


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python check_async_calls.py <path>")
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
        for file_path, line_no, message, _ in violations:
            print(f"{file_path}:{line_no}: {message}")
        print(f"\nFound {len(violations)} violation(s)")
        return 1

    print("No violations found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
