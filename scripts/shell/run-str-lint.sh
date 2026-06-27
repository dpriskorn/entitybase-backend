#!/bin/bash
cd "$(dirname "$0")/../.."
set -Eeuo pipefail

echo "Checking for str | None = Field(default=None) instead of str = Field(default=\"\")..."

poetry run python scripts/linters/check_str_fields.py src/

echo "Str field linting passed!"