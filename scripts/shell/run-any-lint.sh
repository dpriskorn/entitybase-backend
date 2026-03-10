#!/bin/bash
cd "$(dirname "$0")/../.."
set -Eeuo pipefail

echo "Checking for functions returning -> Any..."

poetry run python scripts/linters/check_any_returns.py src/

echo "Any return linting passed!"