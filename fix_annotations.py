#!/usr/bin/env python3
import os
import re


def fix_test_annotations(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    modified = False
    for i, line in enumerate(lines):
        # Match def test_...(): without -> 
        match = re.match(r'^(\s*)def test_[^(]*\([^)]*\):\s*$', line)
        if match and '->' not in line:
            # indent = match.group(1)
            # Insert -> None before :
            lines[i] = line.rstrip()[:-1] + ' -> None:\n'
            modified = True
    
    if modified:
        with open(filepath, 'w') as f:
            f.writelines(lines)
        print(f"Fixed {filepath}")

if __name__ == '__main__':
    for root, dirs, files in os.walk('tests'):
        for file in files:
            if file.endswith('.py'):
                fix_test_annotations(os.path.join(root, file))