docker ps -aq | xargs -r docker stop
docker ps -aq | xargs -r docker rm
docker volume ls -q | xargs -r docker volume rm

echo "✅ All containers stopped and removed"
