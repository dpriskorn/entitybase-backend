#!/bin/bash
cd "$(dirname "$0")/../.."
set -Eeuo pipefail

echo "Checking for multiple status_code asserts in tests..."

poetry run python scripts/linters/status_code_linter.py

echo "Status code assert linting passed!"
