#!/bin/bash
set -e

./update-docs.sh
./run-linters.sh
docker compose --file docker/docker-compose.yml down --remove-orphans -t 0 -v 
nice -20 docker compose --file docker/docker-compose.yml build
docker compose --file docker/docker-compose.yml --progress=plain build
docker compose --file docker/docker-compose.yml up -d
docker logs -f tests