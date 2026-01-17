#!/bin/bash
set -e

echo "Checking for escaped quotes in Python files..."
python scripts/linters/backslash_linter.py src/
echo "Backslash check passed!"