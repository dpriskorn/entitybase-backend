#!/bin/bash
cd "$(dirname "$0")/../.."
set -e

echo "Exporting Poetry dependencies to requirements files..."

# Use poetry from venv if available, otherwise fall back to system
if [ -f ".venv/bin/poetry" ]; then
    POETRY=".venv/bin/poetry"
else
    POETRY="poetry"
fi

# Check if poetry export is available
if $POETRY export --help >/dev/null 2>&1; then
    echo "Using Poetry export command..."
    $POETRY export --format requirements.txt --output requirements.txt --without-hashes
    $POETRY export --format requirements.txt --output requirements-dev.txt --without-hashes --with dev
    $POETRY export --format requirements.txt --output requirements-idworker.txt --without-hashes --with idworker
    $POETRY export --format requirements.txt --output requirements-stats-worker.txt --without-hashes --with stats-worker
    $POETRY export --format requirements.txt --output requirements-json-worker.txt --without-hashes --with json-worker
    $POETRY export --format requirements.txt --output requirements-ttl-worker.txt --without-hashes --with ttl-worker
else
    # Fallback: Use poetry show and format output
    $POETRY show --only main | awk '{print $1"=="$2}' > requirements.txt
    $POETRY show --with dev | awk '{print $1"=="$2}' > requirements-dev.txt
    $POETRY show --with idworker | awk '{print $1"=="$2}' > requirements-idworker.txt
    $POETRY show --with stats-worker | awk '{print $1"=="$2}' > requirements-stats-worker.txt
    $POETRY show --with json-worker | awk '{print $1"=="$2}' > requirements-json-worker.txt
    $POETRY show --with ttl-worker | awk '{print $1"=="$2}' > requirements-ttl-worker.txt
fi

echo "Requirements files updated successfully"