#!/usr/bin/env python3
"""
Script to complete test file updates for configurable API prefix.
This replaces all instances of:
- base_url: str → api_url: str
- f"{base_url}/entitybase/v1/... → f"{api_url}/...
- /entitybase/v1/... (relative paths) → /... (clean paths)
"""
from pathlib import Path

def update_test_files():
    """Update all test files."""
    tests_dir = Path("tests/integration")
    count = 0

    for py_file in tests_dir.rglob("*.py"):
        if py_file.name == "conftest.py":
            continue

        try:
            with open(py_file, 'r') as f:
                content = f.read()

            if 'base_url' not in content and 'entitybase/v1' not in content:
                continue

            original = content

            # Replace parameter names
            content = content.replace(', base_url: str)', ', api_url: str)')
            content = content.replace('(base_url: str)', '(api_url: str)')
            content = content.replace('base_url: str) ->', 'api_url: str) ->')

            # Replace URL patterns
            content = content.replace('f"{base_url}/entitybase/v1', 'f"{api_url}')
            content = content.replace('f"{base_url}/entitybase', 'f"{api_url}')

            # For files that may use different patterns
            content = content.replace('/entitybase/v1/', '/')

            if content != original:
                with open(py_file, 'w') as f:
                    f.write(content)
                count += 1
                print(f"Updated: {py_file.name}")

        except Exception as e:
            print(f"Error: {py_file}: {e}")

    print(f"\nDone! Updated {count} files.")

if __name__ == "__main__":
    update_test_files()