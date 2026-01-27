set -e

if [ "$(docker ps -q | wc -l)" -gt 0 ]; then
  echo "Containers are running"
else
  echo "No containers are running, run ./run-api-local.sh before this"
  exit 1
fi

echo "Running integration tests"
#pytest -m integration

# sdt out / logs
pytest -m integration -s --strict-markers

# stop first failure
#pytest -m integration -x --strict-markers

# verbose
#pytest -m integration -v --strict-markers
