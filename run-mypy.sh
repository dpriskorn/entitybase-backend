#!/bin/bash
set -euo pipefail

source .venv/bin/activate

mypy --cache-dir .mypy_cache --sqlite-cache --explicit-package-bases src/

# slow per file run
#for file in $(find src tests scripts -name "*.py"); do
#    echo "Checking $file"
#    mypy --pretty --show-error-codes --no-error-summary "$file" && continue || exit 1
#done