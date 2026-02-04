"""
Linter to check for 'as' in import statements.
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple, Dict


def load_allowlist() -> Dict[str, List[int]]:
    """Load the allowlist from config/linters/allowlists/custom/as-imports.txt.

    Returns:
        Dict mapping file paths to list of line numbers to allow.
        Patterns without line numbers are stored with an empty list.
    """
    allowlist_path = Path("config/linters/allowlists/custom/as-imports.txt")
    allowlist: Dict[str, List[int]] = {}

    if not allowlist_path.exists():
        return allowlist

    try:
        with open(allowlist_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                if ":" in line:
                    parts = line.split(":")
                    file_path = parts[0]
                    line_no = parts[1]
                    if file_path not in allowlist:
                        allowlist[file_path] = []
                    try:
                        allowlist[file_path].append(int(line_no))
                    except ValueError:
                        pass
                else:
                    allowlist[line] = []
    except Exception:
        pass

    return allowlist


class AsImportChecker(ast.NodeVisitor):
    """AST visitor to check for 'as' in import statements."""

    def __init__(self, source_lines: List[str], file_path: str, allowlist: Dict[str, List[int]]):
        self.source_lines = source_lines
        self.file_path = file_path
        self.allowlist = allowlist
        self.violations: List[Tuple[str, int, str, str]] = []

    def is_allowed(self, line_no: int) -> bool:
        """Check if this line number is allowed for the current file."""
        if self.file_path in self.allowlist:
            allowed_lines = self.allowlist[self.file_path]
            if not allowed_lines:
                return True
            if line_no in allowed_lines:
                return True
        return False

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.asname is not None:
                line_content = self.source_lines[node.lineno - 1].strip()
                if not self.is_allowed(node.lineno) and "# noqa" not in line_content:
                    self.violations.append(
                        (
                            self.file_path,
                            node.lineno,
                            line_content,
                            f"Import with 'as' alias: {alias.name} as {alias.asname}",
                        )
                    )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            if alias.asname is not None:
                line_content = self.source_lines[node.lineno - 1].strip()
                if not self.is_allowed(node.lineno) and "# noqa" not in line_content:
                    self.violations.append(
                        (
                            self.file_path,
                            node.lineno,
                            line_content,
                            f"ImportFrom with 'as' alias: {alias.name} as {alias.asname}",
                        )
                    )
        self.generic_visit(node)


def check_file(file_path: Path, allowlist: Dict[str, List[int]]) -> List[Tuple[str, int, str, str]]:
    """Check a single file for 'as' in imports."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        source_lines = source.splitlines()
        tree = ast.parse(source, filename=str(file_path))
        checker = AsImportChecker(source_lines, str(file_path), allowlist)
        checker.visit(tree)
        return checker.violations
    except SyntaxError:
        return [(str(file_path), 0, "", "Syntax error in file")]


def main(directories: List[str]) -> None:
    """Main function to check all Python files in directories."""
    allowlist = load_allowlist()
    violations = []

    for directory in directories:
        dir_path = Path(directory)
        for py_file in dir_path.rglob("*.py"):
            violations.extend(check_file(py_file, allowlist))

    if violations:
        print("Found 'as' in imports:")
        for file_path, line_no, line_content, message in violations:
            print(f"{file_path}:{line_no}: {message}")
            print(f"  {line_content}")

        allowlist_path = Path("config/linters/allowlists/custom/as-imports.txt")
        print(f"\nTo allowlist violations, add 'file:line' entries to {allowlist_path}:")
        for file_path, line_no, _, _ in violations[:10]:
            print(f"  {file_path}:{line_no}")

        sys.exit(1)
    else:
        print("No 'as' in imports found")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_as_imports.py <directory1> [<directory2> ...]")
        sys.exit(1)
    main(sys.argv[1:])
