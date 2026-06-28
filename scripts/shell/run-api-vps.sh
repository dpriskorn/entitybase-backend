#!/bin/bash
cd "$(dirname "$0")/../.."
set -e

echo "🚀 Starting Docker services (MySQL, rustfs, Redpanda)..."
docker compose -f docker-compose.tests.yml up -d mysql rustfs redpanda

echo "⏳ Waiting for services to be healthy..."
sleep 30

echo "📦 Creating buckets and tables..."
docker compose -f docker-compose.tests.yml up create-buckets create-tables

echo "✅ Setup complete! Starting API..."

source test.env

echo "🐍 Starting API with uvicorn..."
exec poetry run uvicorn models.rest_api.main:app \
  --host 0.0.0.0 \
  --port 8080
