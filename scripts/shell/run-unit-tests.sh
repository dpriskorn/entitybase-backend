#!/bin/bash
cd "$(dirname "$0")/../.."
set -e

find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

poetry run pytest tests/unit/ -n auto
