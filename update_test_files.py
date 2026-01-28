#!/usr/bin/env python3
"""Update test files to use api_url fixture instead of base_url}/entitybase/v1"""

import re
from pathlib import Path

def update_test_file(py_file):
    """Update a test file to use api_url fixture."""
    try:
        with open(py_file, 'r') as f:
            content = f.read()
        
        if 'entitybase/v1' not in content and 'api_url' in content:
            return  # Already updated
        
        if 'entitybase/v1' not in content:
            return  # No changes needed
        
        original_content = content
        
        # Pattern 1: base_url}/entitybase/v1 -> api_url
        # This handles f"{base_url}/entitybase/v1/..." -> f"{api_url}/..."
        content = re.sub(r'(f"{base_url}\})/entitybase/v1', r'f"{api_url}', content)
        
        # Pattern 2: api_client.get("/entitybase/v1/...) -> api_client.get(f"{api_url}/..."
        # These need to be checked and updated properly
        # Since these paths have leading slash, we need to handle them differently
        
        # Check if we changed the API endpoints from relative to absolute
        # Actually, for requests.Session, relative paths won't work with f"{api_url}"
        # The pattern is: f"{base_url}/entitybase/v1/..." becomes f"{api_url}/..."
        # This is the correct pattern. Let me also check for /entitybase/v1 at the start
        
        if content != original_content:
            with open(py_file, 'w') as f:
                f.write(content)
            return True
    
    except Exception as e:
        print(f"Error processing {py_file}: {e}")
        return False
    
    return False

if __name__ == "__main__":
    tests_dir = Path("/home/dpriskorn/src/python/wikibase-backend/tests/integration")
    files_changed = []
    files_skipped = []
    
    for py_file in tests_dir.rglob("*.py"):
        if py_file.name == "conftest.py":
            continue
        
        if update_test_file(py_file):
            files_changed.append(str(py_file.relative_to(tests_dir)))
        elif 'entitybase/v1' in py_file.read_text(encoding='utf-8', errors='ignore'):
            files_skipped.append(str(py_file.relative_to(tests_dir)))
    
    print(f"\nFiles updated: {len(files_changed)}")
    for f in files_changed:
        print(f"  - {f}")
    
    print(f"\nFiles skipped (needs manual review): {len(files_skipped)}")
    for f in files_skipped:
        print(f"  - {f}")