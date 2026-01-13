#!/bin/bash
set -Eeuo pipefail

# Check for Python files with >=900 lines, excluding .venv
long_files=$(find src -name "*.py" ! -path "./.venv/*" -exec wc -l {} \; | awk '$1 >= 900 {print $2 ": " $1 " lines"}')

if [ -n "$long_files" ]; then
    echo "Files with >=900 lines found:"
    echo "$long_files"
    exit 1
else
    echo "No files with >=900 lines found"
fi