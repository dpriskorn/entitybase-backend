#!/usr/bin/env python3
"""Generate git commit statistics."""

import subprocess


def get_commit_count() -> str:
    """Get total number of commits on current branch."""
    cmd = ["git", "rev-list", "--count", "HEAD"]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")
    if result.returncode != 0:
        raise RuntimeError(f"git failed: {result.stderr}")
    return result.stdout.strip()


if __name__ == "__main__":
    count = get_commit_count()
    print(f"# Git Commits\n{count}\n")
