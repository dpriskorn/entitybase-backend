#!/usr/bin/env python3
"""Generate SCC statistics for the codebase, with dynamic src/models subfolders."""

import subprocess
from pathlib import Path


def run_scc(path: str) -> str:
    """Run scc on the given path and return output."""
    cmd = [
        "scc",
        "--no-cocomo",
        "--exclude-dir",
        "mediawiki-extensions-Wikibase",
        "--exclude-dir",
        "test_data",
        "--exclude-dir",
        "disabled_tests",
        path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")
    if result.returncode != 0:
        raise RuntimeError(f"scc failed on {path}: {result.stderr}")
    return result.stdout


def generate_stats() -> str:
    """Generate STATISTICS.md content with dynamic src/models subfolders."""
    content = ""
    # Static sections
    content += "# Overall\n```\n"
    content += run_scc(".")
    content += "```\n\n"

    content += "# src\n```\n"
    content += run_scc("src")
    content += "```\n\n"

    content += "# src/models\n```\n"
    content += run_scc("src/models")
    content += "```\n\n"

    # Dynamic sections for src/models subfolders
    models_dir = Path("src/models")
    if models_dir.exists():
        subfolders = sorted([d for d in models_dir.iterdir() if d.is_dir()])
        for subfolder in subfolders:
            content += f"# src/models/{subfolder.name}\n```\n"
            content += run_scc(str(subfolder))
            content += "```\n\n"

    # Tests section
    content += "# tests\n```\n"
    content += run_scc("tests")
    content += "```\n"

    return content


if __name__ == "__main__":
    print(generate_stats())