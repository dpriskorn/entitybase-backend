#!/bin/bash
set -e

./update-docs.sh
./run-linters.sh
docker compose --file docker/docker-compose.yml down --remove-orphans -t 0 -v 
nice -20 docker compose --file docker/docker-compose.yml build
docker compose --progress=plain build 
docker compose up -d
docker logs -f integration-tests