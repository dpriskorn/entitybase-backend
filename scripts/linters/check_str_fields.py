#!/usr/bin/env python3
"""
Linter to check for str | None = Field(default=None) and suggest str = Field(default="").
"""

import sys
from pathlib import Path


def check_file(file_path: Path) -> list[tuple[str, int, str]]:
    """Check a single Python file for str | None = Field(default=None)."""
    violations = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line_no, line in enumerate(lines, 1):
                stripped = line.strip()
                # Skip comments and empty lines
                if not stripped or stripped.startswith("#"):
                    continue
                # Look for str | None = Field(default=None)
                if "str | None = Field(default=None)" in line:
                    violations.append(
                        (
                            str(file_path),
                            line_no,
                            f"Found 'str | None = Field(default=None)': {line.strip()}, use 'str = Field(default=\"\")' instead",
                        )
                    )
    except Exception as e:
        violations.append((str(file_path), 0, f"Error reading file: {e}"))

    return violations


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python check_str_fields.py <path>")
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
        print("str | None = Field(default=None) violations:")
        for file_path, line_no, message in violations:
            print(f"{file_path}:{line_no}: {message}")
        sys.exit(1)
    else:
        print("No str | None = Field(default=None) violations found")


if __name__ == "__main__":
    main()