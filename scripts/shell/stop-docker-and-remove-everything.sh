#!/bin/bash

# Kill uvicorn on port 8080
fuser -k 8080/tcp 2>/dev/null || true

# Stop and remove Docker containers
docker ps -aq | xargs -r docker stop
docker ps -aq | xargs -r docker rm

# Remove Docker volumes
docker volume ls -q | xargs -r docker volume rm

echo "✅ All containers stopped and removed"
