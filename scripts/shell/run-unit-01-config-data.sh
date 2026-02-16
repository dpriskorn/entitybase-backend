#!/bin/bash
cd "$(dirname "$0")/../.."
set -e

find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

source .venv/bin/activate
export PYTHONPATH=src

echo "Running unit tests (config, data, services, validation, json_parser)"
pytest tests/unit/models/config tests/unit/models/data tests/unit/models/services tests/unit/models/validation tests/unit/models/json_parser -n auto
