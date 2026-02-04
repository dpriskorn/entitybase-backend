#!/usr/bin/env python3
"""
Linter to check for Python files that exceed a configurable line limit.
Usage: python check_long_files.py <path> [line_limit]
"""

import sys
from pathlib import Path


def load_allowlist() -> set[str]:
    """Load the allowlist from config/linters/allowlists/custom/long-files.txt."""
    allowlist_path = Path("config/linters/allowlists/custom/long-files.txt")
    if not allowlist_path.exists():
        return set()
    try:
        with open(allowlist_path, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    except Exception:
        return set()


def check_file(file_path: Path, line_limit: int, allowlist: set[str]) -> tuple[int, str] | None:
    """Check a single Python file for line count violations."""
    if str(file_path) in allowlist:
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            line_count = sum(1 for _ in f)

        if line_count > line_limit:
            return line_count, str(file_path)
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return None

    return None


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python check_long_files.py <path> [line_limit]")
        print("  path: Directory to scan for .py files")
        print("  line_limit: Maximum allowed lines (default: 800)")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Path {path} does not exist")
        sys.exit(1)

    line_limit = 800
    if len(sys.argv) >= 3:
        try:
            line_limit = int(sys.argv[2])
        except ValueError:
            print(f"Invalid line_limit: {sys.argv[2]}. Using default: 800")

    allowlist = load_allowlist()
    violations = []

    if path.is_file() and path.suffix == ".py":
        result = check_file(path, line_limit, allowlist)
        if result:
            violations.append(result)
    elif path.is_dir():
        for py_file in path.rglob("*.py"):
            result = check_file(py_file, line_limit, allowlist)
            if result:
                violations.append(result)

    if violations:
        violations.sort(key=lambda x: x[0], reverse=True)
        print(f"Files exceeding {line_limit} lines:")
        for line_count, file_path in violations:
            print(f"  {file_path}: {line_count} lines")

        allowlist_path = Path("config/linters/allowlists/custom/long-files.txt")
        print(f"\nTo allowlist violations, add files to {allowlist_path}:")
        for _, file_path in violations[:10]:
            print(f"  {file_path}")
        sys.exit(1)
    else:
        print(f"No files exceeding {line_limit} lines found")


if __name__ == "__main__":
    main()
