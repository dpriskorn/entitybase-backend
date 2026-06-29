#!/bin/bash
cd "$(dirname "$0")/../.."
set -e

ENV_FILE="${1:-minimal}"

if [ "$(docker ps -q | wc -l)" -gt 0 ]; then
  echo "Containers are running"
else
  echo "No containers are running, run ./run-api-local.sh before this"
  exit 1
fi

source "test-${ENV_FILE}.env"

echo "Running tests 51-100 (env=${ENV_FILE})"
poetry run pytest tests/integration --capture=no --strict-markers --log-cli-level=DEBUG --log-cli-format="%(asctime)s - %(name)s - %(levelname)s - %(message)s" -k "test_watchlist or test_entity_deletion or test_item_terms" --durations=10
