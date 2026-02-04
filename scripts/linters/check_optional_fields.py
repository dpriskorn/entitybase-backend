#!/usr/bin/env python3
"""
Linter to check for = None assignments in Python files.
"""

import re
import sys
from pathlib import Path


def check_file(file_path: Path) -> list[tuple[str, int, str]]:
    """Check a single Python file for = None."""
    violations = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            if "BaseModel" not in content:
                return violations
            lines = content.splitlines()
            for line_no, line in enumerate(lines, 1):
                stripped = line.strip()
                # Skip comments and empty lines
                if not stripped or stripped.startswith("#"):
                    continue
                # Skip function/method signatures
                if stripped.startswith("def "):
                    continue
                # Skip method-level lines (indented with 8+ spaces)
                if line.startswith("        "):
                    continue
                # Skip function parameter lines (indented 4 spaces with type hints and = None)
                # Pattern: indented 4 spaces, has type annotation, ends with = None or = None,
                # Handles complex nested types like Optional[Callable[[int], None]]
                if line.startswith("    ") and not line.startswith("        "):
                    if re.search(r":\s*.+?\s*=\s*None,?\s*$", line):
                        continue
                # Allowlist upper_bound and lower_bound for QuantityValue
                if "upper_bound" in line or "lower_bound" in line:
                    continue
                # Look for = None
                if " = None" in line:
                    violations.append(
                        (
                            str(file_path),
                            line_no,
                            f"Found '= None' assignment: {line.strip()}, consider using Field() instead",
                        )
                    )
    except Exception as e:
        violations.append((str(file_path), 0, f"Error reading file: {e}"))

    return violations


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python check_optional_fields.py <path>")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Path {path} does not exist")
        sys.exit(1)

    violations = []

    if path.is_file() and path.suffix == ".py":
        if "workers" not in str(path):
            violations.extend(check_file(path))
    elif path.is_dir():
        for py_file in path.rglob("*.py"):
            if "workers" not in str(py_file):
                violations.extend(check_file(py_file))

    if violations:
        print("= None violations:")
        for file_path, line_no, message in violations:
            print(f"{file_path}:{line_no}: {message}")
        sys.exit(1)
    else:
        print("No = None violations found")


if __name__ == "__main__":
    main()
