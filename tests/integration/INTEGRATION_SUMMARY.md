# Redpanda Integration Tests Summary

## Overview

Comprehensive integration tests for Redpanda stream producer and consumer have been added to the project. These tests ensure that publishing events to Redpanda works correctly and covers various scenarios.

## Files Created

### 1. Test Files

#### `tests/integration/test_redpanda_producer.py`
- **11 tests** for the Redpanda producer
- Tests producer lifecycle (start/stop)
- Tests publishing all event types (creation, edit, soft_delete, redirect, unredirect)
- Tests multiple event publishing
- Tests event key extraction and JSON serialization
- Tests health check properties

#### `tests/integration/test_redpanda_consumer.py`
- **10 tests** for the Redpanda consumer
- Tests consumer lifecycle (start/stop)
- Tests consuming single and multiple events
- Tests consuming from different topics
- Tests health check properties
- Tests multiple consumer groups
- Tests consuming late messages
- Tests handling special characters
- Tests connecting to multiple brokers

#### `tests/integration/test_redpanda_e2e.py`
- **6 end-to-end tests** combining producer and consumer
- Tests complete lifecycle with multiple events
- Tests entity deletion workflow
- Tests entity redirection workflow
- Tests entity unredirect workflow
- Tests multiple independent entities
- Tests error handling

### 2. Documentation

#### `tests/integration/README_REDPANDA.md`
- Detailed setup instructions
- Running tests guide
- Configuration details
- Event schema documentation
- Troubleshooting section
- Best practices

#### `run-redpanda-tests.sh`
- Automated test runner script
- Starts Redpanda if not running
- Runs all integration tests
- User-friendly output

## Test Coverage

### Producer Tests
✅ Start and stop producer
✅ Publish creation events
✅ Publish edit events with from_revision_id
✅ Publish soft delete events
✅ Publish redirect and unredirect events
✅ Publish multiple events sequentially
✅ Extract correct event keys
✅ Serialize events to JSON
✅ Handle all change types
✅ Healthy connection checks

### Consumer Tests
✅ Start and stop consumer
✅ Consume single events
✅ Consume multiple events
✅ Consume from different topics
✅ Health check properties
✅ Multiple consumer groups
✅ Consume late messages
✅ Handle special characters
✅ Multiple broker connections
✅ Error handling

### End-to-End Tests
✅ Complete producer-consumer lifecycle
✅ Entity deletion workflow
✅ Entity redirection workflow
✅ Entity unredirect workflow
✅ Multiple independent entities
✅ Error handling

## Event Schema

All published events follow this structure:

```python
{
    "entity_id": str,
    "revision_id": int,
    "change_type": str,
    "changed_at": str,
    "user_id": str,
    "from_revision_id": int | None,
    # Additional fields based on change_type:
    # - soft_delete: delete_type, deletion_reason
    # - redirect/unredirect: redirect_from_id, redirect_to_id
}
```

**Change Types:**
- `creation` - Entity created
- `edit` - Entity edited
- `soft_delete` - Entity soft deleted
- `hard_delete` - Entity hard deleted (if implemented)
- `redirect` - Entity redirected to another
- `unredirect` - Redirect removed

## Running Tests

### Quick Start (Recommended)

```bash
# Make script executable
chmod +x run-redpanda-tests.sh

# Run all Redpanda tests
./run-redpanda-tests.sh
```

### Manual Execution

```bash
# Start Redpanda
docker compose up -d redpanda
sleep 5

# Run producer tests
poetry run pytest tests/integration/test_redpanda_producer.py -v

# Run consumer tests
poetry run pytest tests/integration/test_redpanda_consumer.py -v

# Run e2e tests
poetry run pytest tests/integration/test_redpanda_e2e.py -v

# Run all together
poetry run pytest tests/integration/test_redpanda*.py -v
```

### With Coverage

```bash
poetry run pytest tests/integration/test_redpanda*.py --cov=src/models/infrastructure/stream --cov-report=html
```

## Configuration

Test defaults:
- **Redpanda Host**: `redpanda:9092`
- **Kafka Topic**: `wikibase.entity_change`
- **Test Entity Base**: `Q888888`
- **Test User ID**: `test-user-123`

You can override these in the test files or via environment variables.

## Test Structure

Each test file follows these patterns:

```python
@pytest.mark.asyncio
async def test_producer_publishes_creation_event() -> None:
    """Test that producer publishes creation events with correct structure."""
    # Setup
    config = StreamConfig(bootstrap_servers=[...], topic=...)
    producer = StreamProducerClient(config=config)
    
    # Execute
    await producer.start()
    await producer.publish_change(event_data)
    await consumer.consume_events()
    
    # Verify
    assert received_event.entity_id == expected_id
    assert received_event.revision_id == expected_revision
    # ... more assertions
```

## Integration with Existing Tests

These tests are:
- ✅ **Integration tests** - Use real Redpanda infrastructure
- ✅ **Isolated** - Each test creates its own consumer with unique group IDs
- ✅ **Reusable** - Can be run independently
- ✅ **Well-documented** - Each test has a descriptive docstring
- ✅ **Follows conventions** - Uses pytest-asyncio, proper fixtures

## Troubleshooting

### Redpanda Not Ready
```bash
# Check if Redpanda is running
docker ps | grep redpanda

# Check logs
docker logs redpanda

# Restart
docker compose restart redpanda
```

### Connection Errors
```bash
# Verify port
netstat -an | grep 9092

# Test connectivity
telnet redpanda 9092
```

## Future Enhancements

Potential areas for improvement:
1. Add performance/load tests
2. Add retry logic tests
3. Add error recovery tests
4. Add schema validation tests
5. Add concurrent producer/consumer tests

## Notes

- Tests use 5-10 second timeouts to prevent hanging
- All consumers are properly stopped in `finally` blocks
- Test data uses unique entity IDs to avoid conflicts
- Environment variables can be used to customize configuration
