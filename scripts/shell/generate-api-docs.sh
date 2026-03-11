#!/bin/bash
# Generate API documentation from OpenAPI spec

cd "$(dirname "$0")/../.."

if [ ! -d ".venv" ]; then
    echo "Error: Virtual environment not found at $(pwd)/.venv"
    exit 1
fi

.venv/bin/python scripts/generate_api_docs.py
