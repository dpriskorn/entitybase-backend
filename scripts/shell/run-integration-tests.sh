#!/bin/bash
cd "$(dirname "$0")/../.."
set -e

ENV_FILE="${1:-minimal}"

# Check if test infrastructure is running (MySQL, S3, etc.)
./check-docker-services.sh --env="${ENV_FILE}" --clean-connections

source "test-${ENV_FILE}.env"

echo "Running integration tests (ASGITransport - no server required) (env=${ENV_FILE})"
poetry run pytest tests/integration --capture=no --strict-markers --log-cli-level=DEBUG --log-cli-format="%(asctime)s - %(name)s - %(levelname)s - %(message)s" --durations=10
