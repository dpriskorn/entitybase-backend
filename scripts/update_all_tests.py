#!/usr/bin/env python3
"""
Update test files to use api_url fixture instead of base_url.
Also removes entitybase/v1 prefixes from paths.
"""
from pathlib import Path

def update_test_file(py_file):
    """Update a test file to use api_url."""
    try:
        with open(py_file, 'r') as f:
            content = f.read()

        if 'base_url' not in content and 'entitybase/v1' not in content:
            return False

        if py_file.name == "conftest.py":
            return False

        original = content

        # Replace function parameter: base_url: str → api_url: str
        # Pattern: ", base_url: str)" or ") -> None:\n    base_url: str)"
        content = content.replace(', base_url: str)', ', api_url: str)')
        content = content.replace('(base_url: str)', '(api_url: str)')
        content = content.replace('base_url: str) -> None:', 'api_url: str) -> None:')
        content = content.replace('base_url: str) ->', 'api_url: str) ->')

        # Replace URL patterns
        content = content.replace('f"{base_url}/entitybase/v1', 'f"{api_url}')
        content = content.replace('f"{base_url}/entitybase', 'f"{api_url}')

        if content != original:
            with open(py_file, 'w') as f:
                f.write(content)
            return True

    except Exception as e:
        print(f"Error in {py_file}: {e}")
    return False

if __name__ == "__main__":
    tests_dir = Path("/home/dpriskorn/src/python/wikibase-backend/tests/integration")
    files_updated = []

    for py_file in tests_dir.rglob("*.py"):
        if update_test_file(py_file):
            files_updated.append(str(py_file))
            print(f"Updated: {py_file.name}")

    print(f"\nTotal files updated: {len(files_updated)}")