#!/bin/bash
set -Eeuo pipefail

source .venv/bin/activate

echo "Checking for Optional fields with = None instead of Field()..."

python scripts/linters/check_optional_fields.py src/

echo "Pydantic field linting passed!"