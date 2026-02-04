#!/usr/bin/env python3
"""
Linter to check for escaped quotes in Python files, such as \\"\\"\\" in docstrings.
"""

import re
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.resolve()))

from allowlist_utils import is_line_allowed


def load_allowlist() -> set:
    """Load the backslash allowlist from config/linters/allowlists/custom/backslash.txt."""
    allowlist_path = Path("config/linters/allowlists/custom/backslash.txt")
    allowlist = set()
    if allowlist_path.exists():
        with open(allowlist_path, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    allowlist.add(stripped)
    return allowlist


def check_backslashes(file_path: Path, allowlist: set) -> list[str]:
    violations = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line_no, line in enumerate(lines, 1):
                stripped = line.strip()
                # Skip comments and empty lines
                if not stripped or stripped.startswith("#"):
                    continue
                # Check allowlist
                if is_line_allowed(file_path, line_no, allowlist):
                    continue
                # Check for \\"\\"\\" or similar escaped quotes
                if re.search(r"\\\"\\\"\\\"", line):
                    violations.append(
                        f"{file_path}:{line_no}: Found escaped triple quotes in line: {line.strip()}"
                    )
                # Check for other escaped patterns if needed
                elif re.search(r"\\\"", line) and '"""' not in line:
                    violations.append(
                        f"{file_path}:{line_no}: Found escaped quotes in line: {line.strip()}"
                    )
    except Exception as e:
        violations.append(f"Error reading {file_path}: {e}")

    return violations


def main():
    if len(sys.argv) != 2:
        print("Usage: python backslash_linter.py <path>")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Path {path} does not exist")
        sys.exit(1)

    # Load allowlist
    allowlist = load_allowlist()

    violations = []
    if path.is_file() and path.suffix == ".py":
        violations.extend(check_backslashes(path, allowlist))
    elif path.is_dir():
        for py_file in path.rglob("*.py"):
            violations.extend(check_backslashes(py_file, allowlist))

    if violations:
        for violation in violations:
            print(violation)
        allowlist_path = Path("config/linters/allowlists/custom/backslash.txt")
        print(f"To allowlist violations, add 'file:line' entries to {allowlist_path.resolve()}")
        sys.exit(1)
    else:
        print("No backslash violations found.")


if __name__ == "__main__":
    main()
