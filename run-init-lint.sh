#!/bin/bash
set -Eeuo pipefail

source .venv/bin/activate

echo "Checking for __init__ methods in Pydantic BaseModel subclasses..."

python scripts/linters/pydantic_init_linter.py

echo "Pydantic __init__ linting passed!"