#!/bin/bash
cd "$(dirname "$0")/../.."
set -Eeuo pipefail

echo "Checking for functions returning -> dict..."

poetry run python scripts/linters/check_dict_returns.py src/

echo "Dict return linting passed!"