#!/usr/bin/env python3
"""
Linter to check for tuple() usage in Python files.
"""

import sys
from pathlib import Path


def check_file(file_path: Path) -> list[tuple[str, int, str]]:
    """Check a single Python file for tuple() usage."""
    violations = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                stripped = line.strip()
                # Skip comments and empty lines
                if not stripped or stripped.startswith("#"):
                    continue
                # Look for tuple(
                if "tuple(" in line:
                    violations.append(
                        (
                            str(file_path),
                            line_no,
                            f"Found 'tuple()' usage: {line.strip()}, consider using a tuple literal instead",
                        )
                    )
    except Exception as e:
        violations.append((str(file_path), 0, f"Error reading file: {e}"))

    return violations


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python check_tuple_usage.py <path>")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Path {path} does not exist")
        sys.exit(1)

    violations = []

    if path.is_file() and path.suffix == ".py":
        violations.extend(check_file(path))
    elif path.is_dir():
        for py_file in path.rglob("*.py"):
            violations.extend(check_file(py_file))

    if violations:
        print("tuple() violations:")
        for file_path, line_no, message in violations:
            print(f"{file_path}:{line_no}: {message}")
        allowlist_path = Path("config/allowlists/tuple_allowlist.txt")
        print(f"To allowlist violations, add 'file:line' entries to {allowlist_path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
