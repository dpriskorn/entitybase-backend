#!/usr/bin/env python3
"""
Linter to check for cast() usage in Python files.
"""

import sys
from pathlib import Path


def load_allowlist() -> set:
    """Load the cast allowlist from config/linters/allowlists/cast.txt."""
    allowlist_path = Path("config/linters/allowlists/cast.txt")
    allowlist = set()
    if allowlist_path.exists():
        with open(allowlist_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    allowlist.add(line)
    return allowlist


def check_file(file_path: Path, allowlist: set) -> list[tuple[str, int, str]]:
    """Check a single Python file for cast() usage."""
    violations = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                stripped = line.strip()
                # Skip comments and empty lines
                if not stripped or stripped.startswith("#"):
                    continue
                # Look for cast(
                if "cast(" in line:
                    key = f"{file_path}:{line_no}"
                    if key not in allowlist:
                        violations.append(
                            (
                                str(file_path),
                                line_no,
                                f"Found 'cast()' usage: {line.strip()}, consider using a pydantic model at the origin instead",
                            )
                        )
    except Exception as e:
        violations.append((str(file_path), 0, f"Error reading file: {e}"))

    return violations


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python check_cast_usage.py <path>")
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
            violations.extend(check_file(py_file, allowlist))

    if violations:
        print("cast() violations:")
        for file_path, line_no, message in violations:
            print(f"{file_path}:{line_no}: {message}")
        allowlist_path = Path("config/linters/allowlists/cast.txt")
        print(f"To allowlist violations, add 'file:line' entries to {allowlist_path}")
        sys.exit(1)
    else:
        print("No cast() violations found")


if __name__ == "__main__":
    main()
