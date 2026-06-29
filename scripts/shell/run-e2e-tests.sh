set -e
cd "$(dirname "$0")/../.."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ENV_FILE="${1:-minimal}"

# Check if test infrastructure is running (MySQL, S3, etc.)
"$SCRIPT_DIR/check-docker-services.sh" --env="${ENV_FILE}" --clean-connections

source "$PROJECT_ROOT/test-${ENV_FILE}.env"

echo "Running E2E tests (ASGITransport - no API server required) (env=${ENV_FILE})"
poetry run pytest tests/e2e --capture=no --strict-markers --log-cli-level=DEBUG --log-cli-format="%(asctime)s - %(name)s - %(levelname)s - %(message)s" --durations=10
