#!/bin/bash
cd "$(dirname "$0")/../.."
set -e

source .venv/bin/activate

NO_CACHE=""
if [ "$1" = "--no-cache" ]; then
    NO_CACHE="--no-cache"
    echo "🔧 Building without cache"
fi

./scripts/shell/update-docs.sh
./scripts/shell/stop-docker-and-remove-everything.sh
./scripts/shell/clean-pyc.sh

nice -20 docker compose --file docker-compose.tests.yml build $NO_CACHE
docker compose --file docker-compose.tests.yml up -d
