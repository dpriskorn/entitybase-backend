#!/bin/bash
cd "$(dirname "$0")/../.."
set -Eeuo pipefail

LINE_LIMIT=${LONG_FILES_LIMIT:-800}

echo "Checking for Python files with >${LINE_LIMIT} lines..."

poetry run python scripts/linters/check_long_files.py src/ "$LINE_LIMIT"
poetry run python scripts/linters/check_long_files.py tests/ "$LINE_LIMIT"

echo "Long files linting passed!"
