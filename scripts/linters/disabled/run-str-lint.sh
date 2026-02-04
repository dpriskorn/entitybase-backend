#!/bin/bash
set -Eeuo pipefail

source .venv/bin/activate

echo "Checking for str | None = Field(default=None) instead of str = Field(default=\"\")..."

python scripts/linters/check_str_fields.py src/

echo "Str field linting passed!"