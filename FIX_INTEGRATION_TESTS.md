# Fix for 503 Service Unavailable Errors in Integration Tests

## Problem

Integration tests using `ASGITransport` with `AsyncClient` were failing with **503 Service Unavailable** errors because `app.state.state_handler` was not initialized. The `StartupMiddleware` in `main.py` rejects all requests when `state_handler` is None.

### Error Example
```
DEBUG    models.rest_api.main:main.py:54 Rejecting request to /entitybase/v1/users/99999/watchlist during initialization
INFO     httpx:_client.py:1740 HTTP Request: GET http://test/entitybase/v1/users/99999/watchlist "HTTP/1.1 503 Service Unavailable"
```

## Solution

Added an `initialized_app` fixture in `tests/integration/conftest.py` (lines 398-417) that:

1. Creates a `StateHandler` instance with test settings
2. Calls `start()` to initialize it
3. Assigns it to `app.state.state_handler`
4. Runs before each test (function-scoped, autouse=True)
5. Properly disconnects the handler after each test

### Fixture Code
```python
@pytest.fixture(scope="function", autouse=True)
def initialized_app(vitess_client, s3_client):
    """Initialize the FastAPI app with state_handler for integration tests.

    This fixture ensures that app.state.state_handler is properly initialized
    before each test runs, preventing 503 errors from StartupMiddleware.
    """
    from models.rest_api.main import app
    from models.rest_api.entitybase.v1.handlers.state import StateHandler

    state_handler = StateHandler(settings=settings)
    state_handler.start()

    app.state.state_handler = state_handler

    yield

    if state_handler:
        state_handler.disconnect()
        logger.debug("StateHandler disconnected in initialized_app fixture")
```

## Running Tests

### Prerequisites

Tests require infrastructure services to be running:

```bash
# Start test infrastructure
./run-docker-build-tests.sh
```

This starts: MySQL, Minio (S3), Redpanda (Kafka), and ID Worker.

### Run Tests

```bash
# Run all integration tests
pytest tests/integration -v -m integration

# Run specific test file
pytest tests/integration/models/rest_api/v1/entitybase/test_watchlist.py -v

# Run with coverage
pytest tests/integration -v -m integration --cov=src --cov-report=term-missing
```

## Verification

The fix was verified to prevent 503 errors:

- **Before fix**: All requests return 503 from StartupMiddleware
- **After fix**: Middleware allows requests through (no 503 errors)

## Affected Test Files

The following test files benefit from this fix:
- `tests/integration/models/rest_api/v1/entitybase/test_watchlist.py`
- `tests/integration/models/rest_api/v1/entitybase/test_users.py`
- `tests/integration/models/rest_api/v1/entitybase/entities/test_entity_revert.py`
- `tests/integration/models/rest_api/v1/entitybase/test_endorsements.py`
- `tests/integration/test_app.py`

## Technical Details

### Why ASGITransport Needs This Fix

`ASGITransport` allows testing FastAPI apps without running a server, but it doesn't trigger the application's lifespan context manager. This means `app.state.state_handler` is never set, causing the `StartupMiddleware` to reject all requests with 503.

### Why the Fixture Uses Real Clients

Instead of mocking the clients, the fixture uses the existing `vitess_client` and `s3_client` fixtures to:
1. Maintain test realism
2. Test against actual infrastructure
3. Ensure database and S3 interactions work correctly
4. Catch integration issues early

### Autouse and Scope

- **autouse=True**: Automatically applies to all integration tests
- **scope="function"**: Creates fresh state for each test (prevents test pollution)
- Proper cleanup via `disconnect()` ensures no resource leaks
