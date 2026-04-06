#!/bin/bash
cd "$(dirname "$0")/../.."
set -e

echo "Exporting Poetry dependencies to requirements files..."

POETRY="poetry"

$POETRY export --format requirements.txt --output requirements.txt --without-hashes
$POETRY export --format requirements.txt --output requirements-dev.txt --without-hashes --with dev
$POETRY export --format requirements.txt --output requirements-idworker.txt --without-hashes --with idworker
$POETRY export --format requirements.txt --output requirements-stats-worker.txt --without-hashes --with stats-worker
$POETRY export --format requirements.txt --output requirements-json-worker.txt --without-hashes --with json-worker
$POETRY export --format requirements.txt --output requirements-ttl-worker.txt --without-hashes --with ttl-worker

echo "Requirements files updated successfully"