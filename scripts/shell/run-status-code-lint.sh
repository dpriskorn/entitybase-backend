#!/bin/bash
cd "$(dirname "$0")/../.."
set -Eeuo pipefail

source .venv/bin/activate

echo "Checking for multiple status_code asserts in tests..."

python scripts/linters/status_code_linter.py

echo "Status code assert linting passed!"
