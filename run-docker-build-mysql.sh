#!/bin/bash
set -e

./update-docs.sh
docker compose --file docker-compose.mysql.yml down --remove-orphans -t 0 -v
./clean-pyc.sh
./export-requirements.sh
nice -20 docker compose --file docker-compose.mysql.yml build
docker compose --file docker-compose.mysql.yml up -d