#!/bin/bash
set -Eeuo pipefail

source .venv/bin/activate

echo "Checking for tuple() usage..."

python scripts/linters/check_tuple_usage.py src/

echo "Tuple usage linting passed!"