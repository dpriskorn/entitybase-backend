#!/bin/bash
set -Eeuo pipefail

source .venv/bin/activate

echo "Checking for 'as' in import statements..."

python scripts/linters/check_as_imports.py src/ tests/

echo "As import linting passed!"