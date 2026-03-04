#!/bin/bash
cd "$(dirname "$0")/../.."
set -e

echo "Exporting Poetry dependencies to requirements files..."

# Check if poetry export is available
if poetry export --help >/dev/null 2>&1; then
    echo "Using Poetry export command..."
    poetry export --format requirements.txt --output requirements.txt --without-hashes
    poetry export --format requirements.txt --output requirements-dev.txt --without-hashes --with dev
    poetry export --format requirements.txt --output requirements-idworker.txt --without-hashes --with idworker
    poetry export --format requirements.txt --output requirements-stats-worker.txt --without-hashes --with stats-worker
    poetry export --format requirements.txt --output requirements-json-worker.txt --without-hashes --with json-worker
    poetry export --format requirements.txt --output requirements-ttl-worker.txt --without-hashes --with ttl-worker
else
    # Fallback: Use poetry show and format output
    poetry show --only main | awk '{print $1"=="$2}' > requirements.txt
    poetry show --with dev | awk '{print $1"=="$2}' > requirements-dev.txt
    poetry show --with idworker | awk '{print $1"=="$2}' > requirements-idworker.txt
    poetry show --with stats-worker | awk '{print $1"=="$2}' > requirements-stats-worker.txt
    poetry show --with json-worker | awk '{print $1"=="$2}' > requirements-json-worker.txt
    poetry show --with ttl-worker | awk '{print $1"=="$2}' > requirements-ttl-worker.txt
fi

echo "Requirements files updated successfully"