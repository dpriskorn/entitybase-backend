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

---

## URL Prefix Standards

All ASGITransport tests must use `/v1/entitybase/` prefix:
- ✅ Correct: `/v1/entitybase/users/12345/watchlist`
- ❌ Incorrect: `/entitybase/v1/users/12345/watchlist`

The routing structure is:
```python
# main.py:201
app.include_router(v1_router, prefix=settings.api_prefix)  # /v1/entitybase
```

This means all `v1_router` routes are prefixed with `/v1/entitybase/`.

**Files Fixed:**
- `tests/integration/models/rest_api/v1/entitybase/test_users.py` ✅
- `tests/integration/models/rest_api/v1/entitybase/test_watchlist.py` ✅
- `tests/integration/models/rest_api/v1/entitybase/test_endorsements.py` ✅
- `tests/integration/models/rest_api/v1/entitybase/entities/test_entity_revert.py` ✅

---

## ASGITransport Migration Pattern

When converting `requests.Session` tests to `ASGITransport`, follow this pattern:

### Step 1: Update Imports
```python
# Remove:
import requests

# Add:
from httpx import ASGITransport, AsyncClient
import pytest
```

### Step 2: Update Test Function Signature
```python
# Before:
@pytest.mark.integration
def test_xxx(api_client: requests.Session, api_url: str) -> None:
    # ...

# After:
@pytest.mark.asyncio
@pytest.mark.integration
async def test_xxx() -> None:
    from models.rest_api.main import app
    # ...
```

### Step 3: Wrap in AsyncClient Context
```python
async with AsyncClient(
    transport=ASGITransport(app=app), base_url="http://test"
) as client:
    # Test body with await calls
```

### Step 4: Update HTTP Calls
```python
# Replace:
response = api_client.post(f"{api_url}/path", ...)
response = api_client.get(f"{api_url}/path", ...)

# With:
response = await client.post("/v1/entitybase/path", ...)
response = await client.get("/v1/entitybase/path", ...)
```

### Step 5: Fix URL Paths
```python
# Remove {api_url} variable entirely
# Replace all {api_url}/entities/ with /v1/entitybase/entities/
# Replace all {api_url}/entities/items/ with /v1/entitybase/entities/items/
```

### Complete Example
```python
# BEFORE (requests.Session):
import pytest
import requests

@pytest.mark.integration
def test_create_item(api_client: requests.Session, api_url: str) -> None:
    response = api_client.post(
        f"{api_url}/entities/items",
        json={"id": "Q1", "type": "item", "labels": {"en": {"value": "Test"}},
        headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
    )
    assert response.status_code == 200

# AFTER (ASGITransport):
import pytest
from httpx import ASGITransport, AsyncClient

@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_item() -> None:
    from models.rest_api.main import app
    
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/v1/entitybase/entities/items",
            json={"id": "Q1", "type": "item", "labels": {"en": {"value": "Test"}},
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
```

### Affected Test Files

All 16 `requests.Session` test files have been migrated to ASGITransport:

**Phase 2 (Completed):**
- `tests/integration/models/rest_api/v1/entitybase/entities/test_item_terms.py` ✅

**Phase 3 (Completed):**
- `tests/integration/models/rest_api/v1/entitybase/entities/test_entity_basic.py` ✅
- `tests/integration/models/rest_api/v1/entitybase/entities/test_entity_deletion.py` ✅
- `tests/integration/models/rest_api/v1/entitybase/entities/test_entity_protection.py` ✅
- `tests/integration/models/rest_api/v1/entitybase/entities/test_entities_list.py` ✅
- `tests/integration/models/rest_api/v1/entitybase/entities/test_entity_other.py` ✅
- `tests/integration/models/rest_api/v1/entitybase/entities/test_entity_status.py` ✅
- `tests/integration/models/rest_api/v1/entitybase/entities/test_entity_schema_validation.py` ✅
- `tests/integration/models/rest_api/v1/entitybase/entities/test_entity_revision_retrieval.py` ✅
- `tests/integration/models/rest_api/v1/entitybase/entities/test_entity_revision_s3_storage.py` ✅
- `tests/integration/models/rest_api/v1/entitybase/entities/test_entity_queries.py` ✅
- `tests/integration/models/rest_api/v1/entitybase/entities/test_property_terms.py` ✅
- `tests/integration/models/rest_api/v1/entitybase/statements/test_statement_basic.py` ✅
- `tests/integration/models/rest_api/v1/entitybase/statements/test_statement_batch_and_properties.py` ✅
- `tests/integration/models/rest_api/v1/entitybase/statements/test_statement_update.py` ✅
- `tests/integration/models/rest_api/v1/entitybase/test_entitybase_properties.py` ✅

---

## Running Tests (Updated)

No server required! All integration tests now use ASGITransport:

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
pytest tests/integration/models/rest_api/v1/entitybase/test_users.py -v -m integration

# Run with coverage
pytest tests/integration -v -m integration --cov=src --cov-report=term-missing
```

### Test Architecture

- **No server required**: Tests use `httpx.AsyncClient` with `ASGITransport`
- **Direct app testing**: Tests execute against FastAPI app in-memory
- **Faster execution**: No network overhead or server startup time
- **Consistent approach**: All integration tests use same pattern

