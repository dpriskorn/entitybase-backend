#!/bin/bash
cd "$(dirname "$0")/../.."
set -Eeuo pipefail

echo "=== CI Local Simulation ==="

# Use docker-compose.ci.yml to match CI
COMPOSE_FILE="docker-compose.ci.yml"

echo "🧹 Cleaning up any existing containers..."
docker compose --file "$COMPOSE_FILE" down -v 2>/dev/null || true

echo "📦 Building docker images..."
docker compose --file "$COMPOSE_FILE" build \
  api idworker integration e2e create-buckets create-tables

echo "🚀 Starting infrastructure services..."
docker compose --file "$COMPOSE_FILE" up -d mysql minio redpanda

echo "⏳ Waiting for MySQL..."
until docker compose --file "$COMPOSE_FILE" exec -T mysql mysqladmin ping -h localhost --silent; do
  echo "Waiting for MySQL..."
  sleep 2
done
echo "✅ MySQL is ready"

echo "⏳ Waiting for MinIO..."
until curl -f http://localhost:9000/minio/health/live; do
  echo "Waiting for MinIO..."
  sleep 2
done
echo "✅ MinIO is ready"

echo "⏳ Waiting for Redpanda..."
until docker compose --file "$COMPOSE_FILE" exec -T redpanda rpk cluster health 2>/dev/null | grep -q 'Healthy'; do
  echo "Waiting for Redpanda..."
  sleep 2
done
echo "✅ Redpanda is ready"

echo "🗄️ Setting up database tables..."
docker compose --file "$COMPOSE_FILE" run --rm create-tables

echo "🪣 Setting up S3 buckets..."
docker compose --file "$COMPOSE_FILE" run --rm create-buckets

echo "👷 Starting idworker..."
docker compose --file "$COMPOSE_FILE" up -d idworker

echo "🚀 Starting API..."
docker compose --file "$COMPOSE_FILE" up -d api

echo "⏳ Waiting for API to be healthy..."
TIMEOUT=120
ELAPSED=0
until curl -f http://localhost:8000/health; do
  if [ $ELAPSED -ge $TIMEOUT ]; then
    echo "❌ TIMEOUT waiting for API!"
    echo "=== API logs ==="
    docker compose --file "$COMPOSE_FILE" logs --tail=100 api
    echo "=== idworker logs ==="
    docker compose --file "$COMPOSE_FILE" logs --tail=100 idworker
    echo "=== mysql logs ==="
    docker compose --file "$COMPOSE_FILE" logs --tail=50 mysql
    exit 1
  fi
  echo "Waiting for API... ($ELAPSED/$TIMEOUT s)"
  sleep 2
  ELAPSED=$((ELAPSED + 2))
done
echo "✅ API is ready!"

echo "=== CI simulation complete ==="
echo "Services running:"
docker compose --file "$COMPOSE_FILE" ps
