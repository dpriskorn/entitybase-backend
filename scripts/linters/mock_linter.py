#!/usr/bin/env python3
"""Linter to check for 'mock' usage in integration tests."""

import glob
import re
import sys


def main():
    violations = []
    for filepath in glob.glob("tests/integration/**/*.py", recursive=True):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    if re.search(r"mock", line, re.IGNORECASE):
                        violations.append((filepath, line_num, line.strip()))
        except (IOError, UnicodeDecodeError):
            # Skip unreadable files
            continue

    if violations:
        print("Mock usage violations:")
        for filepath, line_num, line in violations:
            print(
                f"{filepath}:{line_num}:{line} no mocks are allowed for integration tests"
            )
        sys.exit(1)
    else:
        print("No mock violations found")
        sys.exit(0)


if __name__ == "__main__":
    main()
