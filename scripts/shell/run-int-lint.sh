#!/bin/bash
cd "$(dirname "$0")/../.."
set -Eeuo pipefail

echo "Checking for int | None patterns in Python files..."

poetry run python scripts/linters/check_int_fields.py src/

echo "Int field linting passed!"