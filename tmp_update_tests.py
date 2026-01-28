#!/usr/bin/env python3
import itertools
from pathlib import Path

# Path to tests directory
tests_dir = Path("/home/dpriskorn/src/python/wikibase-backend/tests/integration")

for py_file in tests_dir.rglob("*.py"):
    if py_file.name == "conftest.py":
        continue
    
    try:
        with open(py_file, 'r') as f:
            content = f.read()
        
        if 'entitybase/v1' not in content:
            continue
        
        original = content
        
        # Pattern: f"{base_url}/entitybase/v1/ -> f"{api_url}/
        content = content.replace('f"{base_url}/entitybase/v1', 'f"{api_url}')
        
        if content != original:
            with open(py_file, 'w') as f:
                f.write(content)
            print(f"Updated: {py_file}")
    except Exception as e:
        print(f"Error in {py_file}: {e}")

print("Done!")