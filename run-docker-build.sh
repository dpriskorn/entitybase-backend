#!/bin/bash
set -e

./run-linters.sh
docker compose down --remove-orphans -v
nice -20 docker compose build
docker compose up --build -d
docker logs -f integration-tests