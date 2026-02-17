docker stop $(docker ps -aq)
cd "$(dirname "$0")/../.."
docker rm $(docker ps -aq)
docker volume rm $(docker volume ls -q)

if [ ! -d "/tmp/minio-data" ]; then
    echo "❌ /tmp/minio-data not found"
    exit 1
fi
rm -rf /tmp/minio-data/*
echo "🧹 Cleared /tmp/minio-data"

echo "✅ All containers stopped and removed"
