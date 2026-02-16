#!/bin/bash
cd "$(dirname "$0")/../.."
set -e

if [ "$(docker ps -q | wc -l)" -gt 0 ]; then
  echo "Containers are running"
else
  echo "No containers are running, run ./run-api-local.sh before this"
  exit 1
fi

source test.env

echo "Running tests 151-200"
pytest tests/integration --capture=no --strict-markers --log-cli-level=DEBUG --log-cli-format="%(asctime)s - %(name)s - %(levelname)s - %(message)s" -k "test_entity_parsing or test_string_value or test_json_fields or test_internal or test_values" --durations=10