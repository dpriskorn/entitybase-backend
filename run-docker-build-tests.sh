#!/bin/bash
set -e

./update-docs.sh
#docker compose --file docker-compose.tests.yml down --remove-orphans -t 0 -v
./run-docker-stop-and-remove-all.sh
./clean-pyc.sh
./export-requirements.sh
nice -20 docker compose --file docker-compose.tests.yml build
docker compose --file docker-compose.tests.yml up -d