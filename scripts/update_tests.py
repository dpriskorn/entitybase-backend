#!/usr/bin/env python3
"""
Update test files to use api_url fixture.
This handles:
1. Replacing f"{base_url}/entitybase/v1/ with f"{api_url}/
2. Also updates lines like /entitybase/v1/ when used without f-string
"""
from pathlib import Path

def update_file(py_file):
    """Update a test file."""
    try:
        with open(py_file, 'r') as f:
            content = f.read()
        
        if 'entitybase/v1' not in content:
            return
        
        original = content
        
        # Replace f"{base_url}/entitybase/v1/ -> f"{api_url}/
        content = content.replace('f"{base_url}/entitybase/v1', 'f"{api_url}')
        
        # Replace /entitybase/v1/ with / when used in path patterns
        # But only for paths, not in strings/comments
        # Simple pattern: "/entitybase/v1/ -> "/
        content = content.replace('"/entitybase/v1', '"/')
        
        if content != original:
            with open(py_file, 'w') as f:
                f.write(content)
            return True
    except Exception as e:
        print(f"Error in {py_file}: {e}")

if __name__ == "__main__":
    import sys
    
    tests_dir = Path("/home/dpriskorn/src/python/wikibase-backend/tests/integration")
    files_changed = []
    
    for py_file in tests_dir.rglob("*.py"):
        if py_file.name == "conftest.py":
            continue
        if update_file(py_file):
            files_changed.append(str(py_file))
    
    print(f"Files changed: {len(files_changed)}")
    for f in files_changed:
        print(f"  {f}")