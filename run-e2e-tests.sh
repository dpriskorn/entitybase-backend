set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if test infrastructure is running (MySQL, S3, etc.)
"$SCRIPT_DIR/check-docker-services.sh" --clean-connections

source "$SCRIPT_DIR/test.env"

echo "Running E2E tests (ASGITransport - no API server required)"
# sdt out / logs
#pytest -m integration -s --strict-markers

# stop first failure
#pytest -p no:xdist -m integration --exitfirst --capture=no --strict-markers
pytest tests/e2e --capture=no --strict-markers --log-cli-level=DEBUG --log-cli-format="%(asctime)s - %(name)s - %(levelname)s - %(message)s" --durations=10

# verbose
#pytest -m integration -v --strict-markers
