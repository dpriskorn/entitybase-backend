#!/bin/bash
cd "$(dirname "$0")/../.."
# Lint script to check for response_model=dict in FastAPI endpoints

set -e

echo "Checking for response_model=dict in FastAPI endpoints..."

python scripts/linters/check_response_model_in_api_endpoints.py src

echo "Response model linting passed!"