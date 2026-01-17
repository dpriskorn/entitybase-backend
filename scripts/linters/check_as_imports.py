"""
Linter to check for 'as' in import statements.
"""

import ast
import sys
from pathlib import Path
from typing import List, Tuple


class AsImportChecker(ast.NodeVisitor):
    """AST visitor to check for 'as' in import statements."""

    def __init__(self, source_lines: List[str], file_path: str, allowlist: set):
        self.source_lines = source_lines
        self.file_path = file_path
        self.allowlist = allowlist
        self.violations: List[Tuple[str, int, str, str]] = []

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.asname is not None:
                line_content = self.source_lines[node.lineno - 1].strip()
                if (
                    not any(allowed in line_content for allowed in self.allowlist)
                    and "# noqa" not in line_content
                ):
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
                if (
                    not any(allowed in line_content for allowed in self.allowlist)
                    and "# noqa" not in line_content
                ):
                    self.violations.append(
                        (
                            self.file_path,
                            node.lineno,
                            line_content,
                            f"ImportFrom with 'as' alias: {alias.name} as {alias.asname}",
                        )
                    )
        self.generic_visit(node)


def check_file(file_path: Path, allowlist: set) -> List[Tuple[str, int, str, str]]:
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
    allowlist = set()  # Add any allowed patterns if needed
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
        sys.exit(1)
    else:
        print("No 'as' in imports found")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_as_imports.py <directory1> [<directory2> ...]")
        sys.exit(1)
    main(sys.argv[1:])
