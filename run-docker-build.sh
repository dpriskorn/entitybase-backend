#!/bin/bash
set -e

./run-ruff.sh
./run-mypy.sh
./run-vulture.sh
docker compose down --remove-orphans -v
nice -20 docker compose build
docker compose up --build -d
docker logs -f integration-tests