#!/bin/bash
set -e

# Check if test infrastructure is running (MySQL, S3, etc.)
./check-docker-services.sh --clean-connections

source test.env

echo "Running integration tests (ASGITransport - no server required)"
#pytest -m integration

# sdt out / logs
#pytest -m integration -s --strict-markers

# stop first failure
#pytest -p no:xdist -m integration --exitfirst --capture=no --strict-markers
pytest tests/integration --capture=no --strict-markers --log-cli-level=DEBUG --log-cli-format="%(asctime)s - %(name)s - %(levelname)s - %(message)s" --durations=10

# verbose
#pytest -m integration -v --strict-markers
