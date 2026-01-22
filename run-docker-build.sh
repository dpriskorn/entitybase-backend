#!/bin/bash
set -e

# ./update-docs.sh
docker compose --file docker/docker-compose.yml down --remove-orphans -t 0 -v #>/dev/null 2>&1
#docker volume prune -f #>/dev/null 2>&1
#docker volume ls
#docker ps -aq | xargs -r docker rm -f
#docker container ls
# ./run-linters.sh
./clean-pyc.sh
./export-requirements.sh
# with cache
nice -20 docker compose --file docker/docker-compose.yml build # >/dev/null 2>&1
# no cache
# nice -20 docker compose --file docker/docker-compose.yml build --no-cache # >/dev/null 2>&1
docker compose --file docker/docker-compose.yml up -d
# docker logs -f idworker
# docker logs -f tests
