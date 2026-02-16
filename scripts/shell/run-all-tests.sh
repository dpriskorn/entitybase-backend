set -e
cd "$(dirname "$0")/../.."

if [ "$(docker ps -q | wc -l)" -gt 0 ]; then
  echo "Containers are running"
else
  echo "No containers are running, run ./run-api-local.sh before this"
  exit 1
fi

source test.env

echo "Running all tests"
#pytest -m integration

# sdt out / logs
#pytest -m integration -s --strict-markers

# stop first failure
#pytest -p no:xdist -m integration --exitfirst --capture=no --strict-markers
pytest tests/ --capture=no --strict-markers --log-cli-level=DEBUG --log-cli-format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# verbose
#pytest -m integration -v --strict-markers
