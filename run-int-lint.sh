#!/bin/bash
set -Eeuo pipefail

source .venv/bin/activate

echo "Checking for int | None patterns in Python files..."

python scripts/linters/check_int_fields.py src/

echo "Int field linting passed!"