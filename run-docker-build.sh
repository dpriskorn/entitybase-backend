#!/bin/bash
set -e

./run-linters.sh
docker compose --file docker/docker-compose.yml down --remove-orphans -t 0 -v 
nice -20 docker compose --file docker/docker-compose.yml build
docker compose up --build -d
docker logs -f integration-tests