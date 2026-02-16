#!/bin/bash
cd "$(dirname "$0")/../.."
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if test infrastructure is running (MySQL, S3, etc.)
"$SCRIPT_DIR/check-docker-services.sh" --clean-connections

source "$SCRIPT_DIR/test.env"

echo "Running E2E tests - Stage 3: User features"
pytest tests/e2e --capture=no --strict-markers --log-cli-level=DEBUG --log-cli-format="%(asctime)s - %(name)s - %(levelname)s - %(message)s" --durations=10 -k "watchlist_e2e or thanks_e2e or endorsements or user_management_e2e or user_workflow or stats_e2e"
