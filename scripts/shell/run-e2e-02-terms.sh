#!/bin/bash
cd "$(dirname "$0")/../.."
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ENV_FILE="${1:-minimal}"

source "$PROJECT_ROOT/test-${ENV_FILE}.env"
source "$PROJECT_ROOT/e2e.env"

echo "Running E2E tests - Stage 2: Terms (env=${ENV_FILE})"
poetry run pytest tests/e2e --capture=no --strict-markers --log-cli-level=DEBUG --log-cli-format="%(asctime)s - %(name)s - %(levelname)s - %(message)s" --durations=10 -k "item_terms_e2e or property_terms_e2e or lexemes_e2e or lexeme_forms_e2e or lexeme_senses_e2e or redirects_e2e"
