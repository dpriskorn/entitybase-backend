#!/bin/bash
cd "$(dirname "$0")/../.."
set -Eeuo pipefail

source .venv/bin/activate

echo "Checking for data: attributes..."

poetry run python scripts/linters/check_data_usage.py src/

echo "Data attribute linting passed!"