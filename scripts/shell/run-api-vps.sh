#!/bin/bash
cd "$(dirname "$0")/../.."
set -e

source .venv/bin/activate

echo "🚀 Starting Docker services (MySQL, MinIO, Redpanda)..."
docker compose -f docker-compose.tests.yml up -d mysql minio redpanda

echo "⏳ Waiting for services to be healthy..."
sleep 30

echo "📦 Creating buckets and tables..."
docker compose -f docker-compose.tests.yml up create-buckets create-tables

echo "📦 Creating Kafka topics..."
sleep 10
docker compose -f docker-compose.tests.yml up --build create-topics || exit 1

echo "✅ Setup complete! Starting API..."

# Load environment variables
source test.env

# Set PYTHONPATH
export PYTHONPATH=src

echo "🐍 Starting API with uvicorn..."
exec uvicorn models.rest_api.main:app \
  --host 0.0.0.0 \
  --port 8080
