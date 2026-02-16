#!/bin/bash
cd "$(dirname "$0")/../.."
set -e

NO_CACHE=""
if [ "$1" = "--no-cache" ]; then
    NO_CACHE="--no-cache"
    echo "🔧 Building without cache"
fi

./update-docs.sh
./stop-docker-and-remove-everything.sh
./clean-pyc.sh
./export-requirements.sh

# Calculate hash of requirements.txt to force rebuild on dependency changes
REQUIREMENTS_HASH=$(md5sum requirements.txt | awk '{print $1}')
echo "📦 Requirements hash: $REQUIREMENTS_HASH"

# Build with requirements hash as build arg to force rebuild when dependencies change
nice -20 docker compose --file docker-compose.tests.yml build $NO_CACHE --build-arg REQUIREMENTS_HASH=$REQUIREMENTS_HASH
docker compose --file docker-compose.tests.yml up -d
