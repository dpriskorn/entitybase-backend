docker stop $(docker ps -aq)
cd "$(dirname "$0")/../.."
docker rm $(docker ps -aq)
docker volume rm $(docker volume ls -q)
echo "✅ All containers stopped and removed"
