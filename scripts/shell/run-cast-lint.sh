#!/bin/bash
cd "$(dirname "$0")/../.."
set -Eeuo pipefail

source .venv/bin/activate

echo "Checking for cast() usage..."

python scripts/linters/check_cast_usage.py src/

echo "Cast usage linting passed!"