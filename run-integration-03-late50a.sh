#!/bin/bash
set -e

if [ "$(docker ps -q | wc -l)" -gt 0 ]; then
  echo "Containers are running"
else
  echo "No containers are running, run ./run-api-local.sh before this"
  exit 1
fi

export VITESS_HOST=localhost
export VITESS_PORT=3306
export VITESS_DATABASE=entitybase
export VITESS_USER=root
export VITESS_PASSWORD=""
export S3_ENDPOINT=http://localhost:9000
export S3_ACCESS_KEY=fakekey
export S3_SECRET_KEY=fakesecret
export PYTHONPATH=src

echo "Running tests 101-150"
pytest tests/integration --capture=no --strict-markers --log-cli-level=DEBUG --log-cli-format="%(asctime)s - %(name)s - %(levelname)s - %(message)s" -k "test_json_import or test_lexeme or test_entity_base or test_json_parser or test_rest_api" --durations=10