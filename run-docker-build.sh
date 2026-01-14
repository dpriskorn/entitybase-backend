#!/bin/bash
set -e

docker compose --file docker/docker-compose.yml down --remove-orphans -t 0 -v #>/dev/null 2>&1
docker volume prune -f #>/dev/null 2>&1
docker volume ls
# ./run-linters.sh
nice -20 docker compose --file docker/docker-compose.yml build >/dev/null 2>&1
time docker compose --file docker/docker-compose.yml up -d
# docker logs -f idworker
docker logs -f tests
# ./update-docs.sh
