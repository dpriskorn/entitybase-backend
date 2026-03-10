#!/bin/bash
cd "$(dirname "$0")/../.."
set -Eeuo pipefail

echo "Checking for Optional fields with = None instead of Field()..."

poetry run python scripts/linters/check_optional_fields.py src/

echo "Pydantic field linting passed!"