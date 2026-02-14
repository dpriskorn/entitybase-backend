#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if test infrastructure is running (MySQL, S3, etc.)
"$SCRIPT_DIR/check-docker-services.sh" --clean-connections

source "$SCRIPT_DIR/test.env"

echo "Running E2E tests - Stage 2: Terms"
pytest tests/e2e --capture=no --strict-markers --log-cli-level=DEBUG --log-cli-format="%(asctime)s - %(name)s - %(levelname)s - %(message)s" --durations=10 -k "item_terms_e2e or property_terms_e2e or lexemes_e2e or lexeme_forms_e2e or lexeme_senses_e2e or redirects_e2e"
