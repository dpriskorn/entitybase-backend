#!/bin/bash
cd "$(dirname "$0")/../.."
set -Eeuo pipefail

source .venv/bin/activate

LINE_LIMIT=${LONG_FILES_LIMIT:-800}

echo "Checking for Python files with >${LINE_LIMIT} lines..."

python scripts/linters/check_long_files.py src/ "$LINE_LIMIT"
python scripts/linters/check_long_files.py tests/ "$LINE_LIMIT"

echo "Long files linting passed!"
