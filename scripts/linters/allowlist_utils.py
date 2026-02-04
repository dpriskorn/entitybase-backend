#!/usr/bin/env python3
"""
Shared utility functions for linters that work with allowlists.
"""

from pathlib import Path
from typing import Dict, List, Set, Union


def is_line_allowed(
    file_path: str | Path,
    line_no: int,
    allowlist: Set[str] | Dict[str, List[int]],
    tolerance: int = 2,
) -> bool:
    """Check if a line number is allowed within the given tolerance.

    Args:
        file_path: Path to the file being checked
        line_no: Line number being checked
        allowlist: Either a set of "file:line" strings or a dict mapping files to line numbers
        tolerance: Number of lines to allow as variance (default: 2)

    Returns:
        True if the line is allowed (exact match or within tolerance range), False otherwise
    """
    file_path_str = str(file_path)

    if isinstance(allowlist, dict):
        if file_path_str in allowlist:
            allowed_lines = allowlist[file_path_str]
            if not allowed_lines:
                return True
            return any(abs(line_no - allowed_line) <= tolerance for allowed_line in allowed_lines)
        return False

    if isinstance(allowlist, set):
        for entry in allowlist:
            if ":" in entry:
                parts = entry.split(":")
                if len(parts) >= 2:
                    entry_file = parts[0]
                    try:
                        entry_line = int(parts[-1])
                        if entry_file == file_path_str and abs(line_no - entry_line) <= tolerance:
                            return True
                    except ValueError:
                        continue
            elif entry == file_path_str:
                return True

    return False
