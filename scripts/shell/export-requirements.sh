#!/bin/bash
cd "$(dirname "$0")/../.."
set -e

echo "Exporting Poetry dependencies to requirements files..."

# Check if poetry export is available
if poetry export --help >/dev/null 2>&1; then
    echo "Using Poetry export command..."
    poetry export --format requirements.txt --output requirements.txt --without-hashes
    poetry export --format requirements.txt --output requirements-dev.txt --without-hashes --with dev
else
    # Fallback: Use poetry show and format output
    poetry show --only main | awk '{print $1"=="$2}' > requirements.txt
    poetry show --with dev | awk '{print $1"=="$2}' > requirements-dev.txt
fi

echo "Requirements files updated successfully"