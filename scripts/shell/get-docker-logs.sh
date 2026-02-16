docker logs integration 2>&1 | tail -100
cd "$(dirname "$0")/../.."
docker logs api 2>&1 | tail -100
