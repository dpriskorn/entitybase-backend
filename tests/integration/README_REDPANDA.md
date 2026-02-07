# Redpanda Integration Tests

This directory contains integration tests for Redpanda stream producer and consumer.

## Test Files

### Producer Tests (`test_redpanda_producer.py`)
Tests the Redpanda producer's ability to:
- Start and stop the producer
- Publish creation events with correct structure
- Publish edit events with from_revision_id
- Publish soft delete events
- Publish redirect and unredirect events
- Publish multiple events sequentially
- Extract correct event keys
- Serialize events to JSON properly
- Handle all change types

### Consumer Tests (`test_redpanda_consumer.py`)
Tests the Redpanda consumer's ability to:
- Start and stop the consumer
- Consume single and multiple events
- Consume from different topics
- Perform health checks
- Consume events after producer stops
- Support multiple consumer groups
- Consume late messages
- Handle special characters in events
- Connect to multiple brokers

## Prerequisites

To run these integration tests, you need:

1. **Redpanda** running locally or in a test environment
2. **Python 3.13+** with required dependencies

## Setup

### Docker Environment (Recommended)

The simplest way to run these tests is with Docker Compose:

```bash
# Start Redpanda
docker compose up -d redpanda

# Wait for Redpanda to be ready
sleep 5

# Run the tests
poetry run pytest tests/integration/test_redpanda_producer.py -v
poetry run pytest tests/integration/test_redpanda_consumer.py -v
```

### Local Environment

If you're running Redpanda locally:

```bash
# Start Redpanda (must be on port 9092)
redpanda start --overwrite

# Set environment variables
export KAFKA_BOOTSTRAP_SERVERS="localhost:9092"

# Run the tests
poetry run pytest tests/integration/test_redpanda_producer.py -v
poetry run pytest tests/integration/test_redpanda_consumer.py -v
```

## Running Tests

### All Redpanda Tests

```bash
poetry run pytest tests/integration/test_redpanda*.py -v
```

### Specific Test Files

```bash
# Producer tests only
poetry run pytest tests/integration/test_redpanda_producer.py -v

# Consumer tests only
poetry run pytest tests/integration/test_redpanda_consumer.py -v
```

### Specific Test Classes or Methods

```bash
# Test only producer start/stop
poetry run pytest tests/integration/test_redpanda_producer.py::TestProducerIntegration::test_producer_start_and_stop -v

# Test consumer events
poetry run pytest tests/integration/test_redpanda_consumer.py::TestConsumerIntegration::test_consumer_consume_multiple_events -v
```

### With Coverage

```bash
poetry run pytest tests/integration/test_redpanda*.py --cov=src/models/infrastructure/stream --cov-report=html
```

## Test Configuration

The tests use the following constants from the test files:

```python
KAFKA_BOOTSTRAP_SERVERS = "redpanda:9092"
KAFKA_TOPIC = "wikibase.entity_change"
TEST_ENTITY_BASE = "Q888888"
TEST_USER_ID = "test-user-123"
```

You can modify these constants to point to your Redpanda instance.

## Event Schema

The producer publishes events that follow this structure:

```python
{
    "entity_id": str,
    "revision_id": int,
    "change_type": str,
    "changed_at": str,  # ISO 8601 format
    "user_id": str,
    "from_revision_id": int | None,
    # Additional fields based on change_type
}
```

**Change Types:**
- `creation` - Entity was created
- `edit` - Entity was edited
- `soft_delete` - Entity was soft deleted
- `hard_delete` - Entity was hard deleted (if implemented)
- `redirect` - Entity was made into a redirect
- `unredirect` - Redirect was removed

## Troubleshooting

### Redpanda Not Ready

If tests timeout waiting for Redpanda, ensure it's running:

```bash
# Check Redpanda status
docker ps | grep redpanda

# Check Redpanda logs
docker logs redpanda

# Restart if needed
docker compose restart redpanda
```

### Connection Errors

If you see connection errors:

```bash
# Verify Redpanda is listening on port 9092
netstat -an | grep 9092

# Check if firewalls are blocking the connection
telnet localhost 9092
```

### Permission Issues

If you get permission errors:

```bash
# Ensure you have proper permissions
chmod +x run-tests.sh
```

## Best Practices

1. **Clean Up**: After running tests, ensure Redpanda is properly stopped if running in containers
2. **Isolation**: Each test creates fresh consumers with unique group IDs
3. **Timeouts**: Tests use 5-10 second timeouts to prevent hanging
4. **Cleanup**: Consumers should be stopped after use to release resources

## Contributing

When adding new tests:

1. Follow the existing test structure
2. Use descriptive test names
3. Include assertions for all important aspects
4. Test both success and edge cases
5. Consider cleanup in `finally` blocks
