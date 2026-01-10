#!/usr/bin/env python3
"""
Script to extract all FastAPI endpoints from the REST API directory.
"""

import re
from pathlib import Path


def extract_endpoints_from_file(file_path):
    """Extract FastAPI endpoints from a Python file."""
    endpoints = []

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Determine prefix based on file path
    file_str = str(file_path)
    if "wikibase/v1" in file_str:
        prefix = "/wikibase/v1"
    elif "v1" in file_str:
        prefix = "/entitybase/v1"
    else:
        prefix = ""

    # Find all router decorators
    pattern = (
        r'@router\.(get|post|put|delete|patch|head|options)\s*\(\s*["\']([^"\']+)["\']'
    )
    matches = re.findall(pattern, content)

    for method, path in matches:
        full_path = prefix + path
        endpoints.append(
            {
                "method": method.upper(),
                "path": path,
                "full_path": full_path,
                "file": str(file_path.relative_to(Path(__file__).parent.parent)),
            }
        )

    return endpoints


def main():
    """Main function to extract all endpoints."""
    rest_api_dir = Path(__file__).parent.parent / "src" / "models" / "rest_api"

    if not rest_api_dir.exists():
        print(f"REST API directory not found: {rest_api_dir}")
        return

    all_endpoints = []

    # Find all Python files in the REST API directory
    for py_file in rest_api_dir.rglob("*.py"):
        if py_file.is_file():
            endpoints = extract_endpoints_from_file(py_file)
            all_endpoints.extend(endpoints)

    # Sort by file, then by path
    all_endpoints.sort(key=lambda x: (x["file"], x["path"]))

    # Print results
    print("# REST API Endpoints\n")
    print("| Method | Path | Full Path | File |")
    print("|--------|------|-----------|------|")

    current_file = None
    for endpoint in all_endpoints:
        if endpoint["file"] != current_file:
            if current_file is not None:
                print()  # Add blank line between files
            current_file = endpoint["file"]
            print(f"**{current_file}:**")

        print(
            f"| {endpoint['method']} | `{endpoint['path']}` | `{endpoint['full_path']}` | {endpoint['file']} |"
        )

    print(f"\nTotal endpoints found: {len(all_endpoints)}")


if __name__ == "__main__":
    main()
