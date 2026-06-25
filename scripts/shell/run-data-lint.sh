#!/bin/bash
cd "$(dirname "$0")/../.."
set -Eeuo pipefail

echo "Checking for data: attributes..."

poetry run python scripts/linters/check_data_usage.py src/

echo "Data attribute linting passed!"