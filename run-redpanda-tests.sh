#!/bin/bash
# Test runner script for Redpanda integration tests

set -e

REDPANDA_HOST="${REDPANDA_HOST:-redpanda:9092}"
KAFKA_TOPIC="${KAFKA_TOPIC:-wikibase.entity_change}"

echo "Starting Redpanda Integration Tests"
echo "====================================="
echo "Redpanda Host: $REDPANDA_HOST"
echo "Kafka Topic: $KAFKA_TOPIC"
echo ""

# Start Redpanda if it's not running
if ! docker ps --format '{{.Names}}' | grep -q redpanda; then
    echo "Redpanda is not running. Starting with Docker Compose..."
    docker compose up -d redpanda

    echo "Waiting for Redpanda to be ready..."
    for i in {1..30}; do
        if docker exec redpanda rpk list topics 2>/dev/null | grep -q "$KAFKA_TOPIC"; then
            echo "Redpanda is ready!"
            break
        fi
        echo "Waiting... ($i/30)"
        sleep 2
    done
else
    echo "Redpanda is already running"
fi

echo ""
echo "Running Producer Tests"
echo "====================="
poetry run pytest tests/integration/test_redpanda_producer.py -v

echo ""
echo "Running Consumer Tests"
echo "====================="
poetry run pytest tests/integration/test_redpanda_consumer.py -v

echo ""
echo "Running End-to-End Tests"
echo "========================"
poetry run pytest tests/integration/test_redpanda_e2e.py -v

echo ""
echo "All Redpanda integration tests completed!"
