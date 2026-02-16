#!/bin/bash
cd "$(dirname "$0")/../.."
set -e

find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

source .venv/bin/activate
export PYTHONPATH=src

echo "Running unit tests (rest_api)"
pytest tests/unit/models/rest_api -n auto
