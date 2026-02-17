docker ps -aq | xargs -r docker stop
docker ps -aq | xargs -r docker rm
docker volume ls -q | xargs -r docker volume rm

if [ ! -d "/tmp/minio-data" ]; then
    echo "❌ /tmp/minio-data not found"
    exit 1
fi
rm -rf /tmp/minio-data/*
echo "🧹 Cleared /tmp/minio-data"

echo "✅ All containers stopped and removed"
