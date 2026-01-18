#!/usr/bin/env python3
"""Update src/schemas/README.md with current schema versions."""

import os
from pathlib import Path
from typing import Dict, List


def find_schema_versions(schemas_dir: Path) -> Dict[str, str]:
    """Find latest version for each schema type."""
    versions = {}

    for root, dirs, files in os.walk(schemas_dir):
        rel_path = Path(root).relative_to(schemas_dir)
        if "latest" in rel_path.parts:
            continue  # Skip latest directories

        # Check if there's a schema file
        schema_file = None
        for file in files:
            if file.endswith((".json", ".yaml")) and "schema" in file:
                schema_file = file
                break

        if schema_file and len(rel_path.parts) >= 2:
            # Schema type is path without version, e.g., entitybase/s3/statement
            schema_type = str(rel_path.parent)
            version = rel_path.parts[-1]
            if schema_type not in versions:
                versions[schema_type] = {}
            versions[schema_type][version] = version

    # Find latest for each type
    latest_versions = {}
    for schema_type, vers in versions.items():
        if vers:
            latest_ver = max(vers.keys(), key=lambda x: [int(i) for i in x.split(".")])
            latest_versions[schema_type] = latest_ver

    return latest_versions


def update_readme(schemas_dir: Path, latest_versions: Dict[str, str]):
    """Update the README.md with latest versions."""
    readme_path = schemas_dir / "README.md"

    if not readme_path.exists():
        print(f"README.md not found at {readme_path}")
        return

    with open(readme_path, "r") as f:
        content = f.read()

    # Update version strings in the content
    for schema_type, latest_ver in latest_versions.items():
        # Look for patterns like "Versions: `1.0.0`, `2.0.0` (latest: `2.0.0`)"
        import re

        pattern = rf"(Versions:.*?)\(latest: `[^`]+`\)"

        def replace_latest(match):
            prefix = match.group(1)
            return f"{prefix}(latest: `{latest_ver}`)"

        content = re.sub(pattern, replace_latest, content, flags=re.MULTILINE)

    with open(readme_path, "w") as f:
        f.write(content)

    print(f"Updated README.md with latest versions: {latest_versions}")


if __name__ == "__main__":
    schemas_dir = Path(__file__).parent.parent.parent / "src" / "schemas"
    latest_versions = find_schema_versions(schemas_dir)
    update_readme(schemas_dir, latest_versions)
