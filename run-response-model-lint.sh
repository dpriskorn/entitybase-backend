#!/bin/bash
# Lint script to check for response_model=dict in FastAPI endpoints

set -e

echo "Checking for response_model=dict in FastAPI endpoints..."

python scripts/lint/check_response_model.py src

echo "Response model linting passed!"