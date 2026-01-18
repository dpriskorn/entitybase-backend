docker compose -f docker/docker-compose.yml rm -f integration
docker compose -f docker/docker-compose.yml up --build integration
