#!/bin/bash
set -e

# ./update-docs.sh
./run-linters.sh
docker compose --file docker/docker-compose.yml down --remove-orphans -t 0 -v 
docker volume prune -f
nice -20 docker compose --file docker/docker-compose.yml build --quiet
docker compose --file docker/docker-compose.yml --progress=plain build
time docker compose --file docker/docker-compose.yml up -d
# docker logs -f idworker
# docker logs -f tests