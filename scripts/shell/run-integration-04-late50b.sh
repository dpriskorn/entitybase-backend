#!/bin/bash
cd "$(dirname "$0")/../.."
set -e

if [ "$(docker ps -q | wc -l)" -gt 0 ]; then
  echo "Containers are running"
else
  echo "No containers are running, run 'make api' before this"
  exit 1
fi

source test.env

echo "Running tests 151-200"
pytest tests/integration --capture=no --strict-markers --log-cli-level=DEBUG --log-cli-format="%(asctime)s - %(name)s - %(levelname)s - %(message)s" -k "test_cas_update or test_create_revision or test_create_with_cas or test_entity_history or test_entity_retrieval or test_get_content_hash or test_get_head_revision or test_hard_delete or test_insert_revision or test_read_revision or test_soft_delete" --durations=10
