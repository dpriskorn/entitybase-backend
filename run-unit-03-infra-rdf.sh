#!/bin/bash
set -e

find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

source .venv/bin/activate
export PYTHONPATH=src

echo "Running unit tests (infrastructure, rdf_builder)"
pytest tests/unit/models/infrastructure tests/unit/models/rdf_builder -n auto
