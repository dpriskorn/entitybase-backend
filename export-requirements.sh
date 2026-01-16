#!/bin/bash
set -e

echo "Exporting Poetry dependencies to requirements files..."

# Export main dependencies
poetry export --output requirements.txt --without-hashes

# Export dev dependencies
poetry export --group dev --output requirements-dev.txt --without-hashes

echo "Requirements files updated successfully"