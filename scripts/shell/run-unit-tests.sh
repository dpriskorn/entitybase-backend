#!/bin/bash
cd "$(dirname "$0")/../.."

find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

source .venv/bin/activate
export PYTHONPATH=src
pytest tests/unit/ -n auto
