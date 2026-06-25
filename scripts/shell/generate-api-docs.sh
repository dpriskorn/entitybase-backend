#!/bin/bash
# Generate API documentation from OpenAPI spec

cd "$(dirname "$0")/../.."

poetry run python scripts/generate_api_docs.py
