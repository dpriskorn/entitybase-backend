#!/bin/bash
set -e

# ./update-docs.sh
./run-linters.sh
docker compose --file docker/docker-compose.yml down --remove-orphans -t 0 -v >/dev/null 2>&1
docker volume prune -f >/dev/null 2>&1
nice -20 docker compose --file docker/docker-compose.yml build >/dev/null 2>&1
time docker compose --file docker/docker-compose.yml up -d
# docker logs -f idworker
# docker logs -f tests