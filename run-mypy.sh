#!/bin/bash
set -euo pipefail

source .venv/bin/activate

for file in $(find src tests scripts -name "*.py"); do
    echo "Checking $file"
    mypy --pretty --show-error-codes --no-error-summary "$file" && continue || exit 1
done