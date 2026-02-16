#!/bin/bash
cd "$(dirname "$0")/../.."
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if test infrastructure is running (MySQL, S3, etc.)
"$SCRIPT_DIR/check-docker-services.sh" --clean-connections

source "$SCRIPT_DIR/test.env"

echo "Running E2E tests - Stage 4: Advanced features"
pytest tests/e2e --capture=no --strict-markers --log-cli-level=DEBUG --log-cli-format="%(asctime)s - %(name)s - %(levelname)s - %(message)s" --durations=10 -k "hash_resolution_e2e or entity_statements_e2e or batch_operations_e2e or hash_operations_e2e or health_import_e2e or json_dump_worker_e2e or revision_with_content_hash"
