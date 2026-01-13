#!/bin/bash
set -Eeuo pipefail

source .venv/bin/activate

echo "Checking for Optional[int] = Field(default=None)"

python scripts/linters/check_int_fields.py src/

echo "Int field linting passed!"