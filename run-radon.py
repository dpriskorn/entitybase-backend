#!/usr/bin/env python3
"""
run-radon.py - Check for duplicate method names across files
"""

import argparse
import ast
import os
import sys
from collections import defaultdict

def load_allowlist(filepath):
    """Load method names from allowlist file"""
    allowlist = set()
    
    # Default common names
    default_allowlist = {
        '__init__', '__str__', '__repr__', '__eq__', '__hash__', 
        '__len__', '__getitem__', '__setitem__', '__delitem__',
        '__enter__', '__exit__', '__call__', '__iter__', '__next__',
        'setUp', 'tearDown', 'main'
    }
    
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith('#'):
                        allowlist.add(line)
            print(f"Loaded {len(allowlist)} method names from allowlist: {filepath}")
        except Exception as e:
            print(f"Warning: Could not read allowlist file {filepath}: {e}", file=sys.stderr)
            return default_allowlist
    else:
        print(f"No allowlist file found at {filepath}, using defaults only")
        return default_allowlist
    
    # Combine with defaults
    return allowlist.union(default_allowlist)

def find_duplicate_methods(directory, allowlist_file, exclude_dirs):
    """Find duplicate method names across Python files"""
    methods = defaultdict(list)
    
    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        tree = ast.parse(f.read(), filename=filepath)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            # Store function name with file location
                            key = f"{node.name}"
                            methods[key].append((filepath, node.lineno))
                except Exception as e:
                    print(f"Warning: Could not parse {filepath}: {e}", file=sys.stderr)
    
    duplicates_found = False
    
    # Load allowlist from file
    allowed_names = load_allowlist(allowlist_file)
    
    for method, locations in sorted(methods.items()):
        if len(locations) > 1:
            # Skip allowed method names
            if method in allowed_names:
                continue
            
            # Skip test methods (starting with test_)
            if method.startswith('test_'):
                continue
            
            duplicates_found = True
            print(f"\n❌ Duplicate method '{method}' found in {len(locations)} locations:")
            for filepath, lineno in locations:
                rel_path = os.path.relpath(filepath)
                print(f"   {rel_path}:{lineno}")
    
    return duplicates_found

def main():
    parser = argparse.ArgumentParser(
        description='Check for duplicate method names across Python files',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'directory',
        nargs='?',
        default='.',
        help='Directory to scan for Python files (default: current directory)'
    )
    parser.add_argument(
        '--allow-list',
        default='.radon-allowlist.txt',
        help='Path to allowlist file (default: .radon-allowlist.txt)'
    )
    parser.add_argument(
        '--exclude',
        action='append',
        default=None,
        help='Directory names to exclude (can be used multiple times, default: .venv)'
    )
    
    args = parser.parse_args()
    
    # Set default excludes if none provided
    if args.exclude is None:
        exclude_dirs = {'.venv'}
    else:
        exclude_dirs = set(args.exclude)
    
    print(f"Checking for duplicate methods in: {args.directory}")
    print(f"Excluding directories: {', '.join(sorted(exclude_dirs))}")
    print("----------------------------------------")
    
    if find_duplicate_methods(args.directory, args.allow_list, exclude_dirs):
        sys.exit(1)
    else:
        print("\n✅ No duplicate methods found")
        sys.exit(0)

if __name__ == "__main__":
    main()