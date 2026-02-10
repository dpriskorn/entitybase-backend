set -e

# Check if test infrastructure is running (MySQL, S3, etc.)
if ! docker ps | grep -q vitess; then
    echo "❌ Test infrastructure not running. Run ./run-docker-build-tests.sh first"
    exit 1
fi
echo "✅ Test infrastructure is running"

source test.env

echo "Running E2E tests (ASGITransport - no server required)"
#pytest -m integration

# sdt out / logs
#pytest -m integration -s --strict-markers

# stop first failure
#pytest -p no:xdist -m integration --exitfirst --capture=no --strict-markers
pytest tests/e2e --capture=no --strict-markers --log-cli-level=DEBUG --log-cli-format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# verbose
#pytest -m integration -v --strict-markers
