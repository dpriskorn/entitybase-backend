#!/bin/bash
cd "$(dirname "$0")/../.."

# Kill uvicorn on port 8080
fuser -k 8080/tcp 2>/dev/null || true

# Stop and remove Docker containers managed by docker-compose.tests.yml
docker compose -f docker-compose.tests.yml down

echo "✅ Containers from docker-compose.tests.yml stopped and removed"
