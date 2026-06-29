set -e
cd "$(dirname "$0")/../.."

ENV_FILE="${1:-minimal}"
shift  # Remove first arg so $1 is now the test path

if [ "$(docker ps -q | wc -l)" -gt 0 ]; then
  echo "Containers are running"
else
  echo "No containers are running, run ./run-api-local.sh before this"
  exit 1
fi

source "test-${ENV_FILE}.env"

echo "Running single test using a single worker (env=${ENV_FILE})"
env | grep -E "^(DB_TYPE|MYSQL|S3)"
poetry run pytest --log-cli-level=DEBUG --log-cli-format="%(asctime)s - %(name)s - %(levelname)s - %(message)s" $1
