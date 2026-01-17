#!/usr/bin/env python3
"""
Linter to check for escaped quotes in Python files, such as \\\"\\\"\\\" in docstrings.
"""

import re
import sys
from pathlib import Path


def load_allowlist(allowlist_path: Path) -> set[str]:
    allowlist = set()
    if allowlist_path.exists():
        with open(allowlist_path, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    allowlist.add(stripped)
    return allowlist


def check_backslashes(file_path: Path, allowlist: set[str]) -> list[str]:
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
                key = f"{file_path}:{line_no}"
                if key in allowlist:
                    continue
                # Check for \\\"\\\"\\\" or similar escaped quotes
                if re.search(r'\\\\"\\\\"\\\\"', line):
                    violations.append(
                        f"{file_path}:{line_no}: Found escaped triple quotes in line: {line.strip()}"
                    )
                # Check for other escaped patterns if needed
                elif re.search(r'\\\\"', line) and '"""' not in line:
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
    allowlist_path = Path("config/linters/allowlists/backslash.txt")
    allowlist = load_allowlist(allowlist_path)

    violations = []
    if path.is_file() and path.suffix == ".py":
        violations.extend(check_backslashes(path, allowlist))
    elif path.is_dir():
        for py_file in path.rglob("*.py"):
            violations.extend(check_backslashes(py_file, allowlist))

    if violations:
        for violation in violations:
            print(violation)
        sys.exit(1)
    else:
        print("No backslash violations found.")


if __name__ == "__main__":
    main()