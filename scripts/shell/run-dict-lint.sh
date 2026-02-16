#!/bin/bash
cd "$(dirname "$0")/../.."
set -Eeuo pipefail

source .venv/bin/activate

echo "Checking for functions returning -> dict..."

python scripts/linters/check_dict_returns.py src/

echo "Dict return linting passed!"