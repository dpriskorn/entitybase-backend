#!/bin/bash
set -e

echo "Exporting Poetry dependencies to requirements files..."

# Export main dependencies
poetry export --format requirements.txt --output requirements.txt --without-hashes

# Export dev dependencies
poetry export --format requirements.txt --output requirements-dev.txt --without-hashes --with dev

echo "Requirements files updated successfully"