#!/bin/bash
cd "$(dirname "$0")/../.."
set -Eeuo pipefail

echo "Checking for __init__ methods in Pydantic BaseModel subclasses..."

poetry run python scripts/linters/pydantic_init_linter.py

echo "Pydantic __init__ linting passed!"