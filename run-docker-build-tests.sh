#!/bin/bash
set -e

./update-docs.sh
#docker compose --file docker-compose.tests.yml down --remove-orphans -t 0 -v
./stop-docker-and-remove-everything.sh
./clean-pyc.sh
./export-requirements.sh
nice -20 docker compose --file docker-compose.tests.yml build
docker compose --file docker-compose.tests.yml up -d
