#!/bin/bash
cd "$(dirname "$0")/../.."
set -Eeuo pipefail

source .venv/bin/activate

echo "Checking for functions returning -> Any..."

python scripts/linters/check_any_returns.py src/

echo "Any return linting passed!"