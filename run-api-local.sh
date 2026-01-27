#!/usr/bin/env bash
set -e

#echo "🚀 Starting dependency containers..."
#docker compose -f docker-compose.deps.yml up -d
#
#echo "⏳ Waiting for services to become healthy..."
#
#wait_for() {
#  local name=$1
#  local url=$2
#
#  echo -n "  - $name"
#  until curl -fs "$url" >/dev/null; do
#    echo -n "."
#    sleep 2
#  done
#  echo " ✅"
#}
#
#wait_for "MinIO" "http://localhost:9000/minio/health/live"
#wait_for "MySQL" "http://localhost:3306"
#wait_for "API deps" "http://localhost:8080/health" || true
#
#echo "✅ All dependencies ready"

./run-docker-build-tests.sh
echo "✅ All dependencies ready"

echo "📦 Exporting environment variables..."

export S3_ENDPOINT="http://localhost:9000"
export S3_ACCESS_KEY="fakekey"
export S3_SECRET_KEY="fakesecret"
export S3_BUCKET="testbucket"

export VITESS_HOST="localhost"
export VITESS_PORT="3306"
export VITESS_DATABASE="entitybase"
export VITESS_USER="root"
export VITESS_PASSWORD=""

export ENTITY_JSON_VERSION="2.0.0"
export S3_REVISION_VERSION="3.0.0"
export S3_STATEMENT_VERSION="1.0.0"
export S3_QUALIFIER_VERSION="1.0.0"
export S3_REFERENCE_VERSION="1.0.0"
export S3_SNAK_VERSION="1.0.0"
export S3_SITELINK_VERSION="1.0.0"

export STREAMING_ENTITYCHANGE_VERSION="1.0.0"
export STREAMING_ENDORSECHANGE_VERSION="1.0.0"
export STREAMING_NEWTHANK_VERSION="1.0.0"
export STREAMING_ENTITY_CHANGE_VERSION="1.0.0"
export STREAMING_ENTITY_DIFF_VERSION="2.0.0"

export STREAMING_ENABLED="false"
export KAFKA_BROKERS="localhost:9092"
export KAFKA_ENTITY_CHANGE_TOPIC="wikibase.entity_change"
export KAFKA_ENTITY_DIFF_TOPIC="wikibase.entity_diff"

export LOG_LEVEL="DEBUG"
export ENVIRONMENT="dev"
export USER_AGENT="Entitybase/1.0 User:So9q"

export PYTHONPATH=src

echo "🐍 Starting API with uvicorn..."
exec uvicorn models.rest_api.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload
