set -e

if [ "$(docker ps -q | wc -l)" -gt 0 ]; then
  echo "Containers are running"
else
  echo "No containers are running, run ./run-api-local.sh before this"
  exit 1
fi

export VITESS_HOST=localhost
export VITESS_PORT=3306
export VITESS_DATABASE=entitybase
export VITESS_USER=root
export VITESS_PASSWORD=""
export PYTHONPATH=src

echo "Running single test using a single worker"

pytest -n 0 $1
