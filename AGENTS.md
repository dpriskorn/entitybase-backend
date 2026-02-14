# Agent Instructions for Wikibase Backend

This document provides guidelines and commands for agentic coding assistants working on the Wikibase Backend project.

## Specialized Documentation

For domain-specific guidance, see these AGENTS.md files:
- [tests/AGENTS.md](tests/AGENTS.md) - Testing patterns, conventions, and best practices
- [scripts/linters/AGENTS.md](scripts/linters/AGENTS.md) - Creating and maintaining custom linters

## Code Style Guidelines

### Python Version and Dependencies
- **Python**: >= 3.13, < 4.0
- **Package Manager**: Poetry
- **Key Dependencies**: FastAPI, Pydantic v2, boto3, uvicorn, rdflib

### Imports
```python
# Standard library imports first
from typing import Any, Dict, List
from pathlib import Path
from collections.abc import AsyncGenerator

# Third-party imports
from fastapi import FastAPI
from pydantic import BaseModel

# Local imports (use relative imports within packages)
from models.internal_representation.values import StringValue
from models.internal_representation.json_fields import JsonField
```

### Naming Conventions

#### Classes
```python
# PascalCase for classes
class EntityParser:
    pass

class TestJsonImportIntegration:  # Test classes
    pass
```

#### Functions and Variables
```python
# snake_case for functions and variables
def parse_string_value(datavalue: dict[str, Any]) -> StringValue:
    pass

def test_lexeme_l42_processing():  # Test functions
    pass

# Constants in UPPER_SNAKE_CASE
JSON_FIELD_VALUE = "value"
```

#### Files and Modules
```python
# snake_case for file names
string_value_parser.py
entity_parser.py

# Test files
test_lexeme_processing.py
test_json_import.py
```

### Type Hints
```python
# Use modern type hints (Python 3.9+ style where possible)
def parse_string_value(datavalue: dict[str, Any]) -> StringValue:
    pass

# Use Union for multiple types
from typing import Union
value: Union[str, int, None]

# Use generics
from typing import List, Dict
entities: List[Dict[str, Any]]
```

### Docstrings
```python
# Use triple quotes for docstrings
def parse_string_value(datavalue: dict[str, Any]) -> StringValue:
    """Parse string value from Wikidata JSON format."""
    pass

# Class docstrings
class EntityParser:
    """Handles parsing of Wikidata entities from JSON."""
    pass
```

### Error Handling

#### Validation Errors
**Always use `raise_validation_error()` instead of raising `ValidationError` directly**:
```python
from models.rest_api.utils import raise_validation_error

# Correct: HTTP-aware error handling
raise_validation_error("Invalid input data", status_code=400)

# Incorrect: Direct ValidationError
raise ValidationError("Invalid input data")
```

#### Repository Methods
```python
def insert_backlink_statistics(self, conn, date, total_backlinks, ...):
    if not isinstance(date, str) or len(date) != 10:
        raise_validation_error(
            f"Invalid date format: {date}. Expected YYYY-MM-DD",
            status_code=400
        )
```

#### Integer Sentinel Values
**Use `0` instead of `None` for integer return types when `None` indicates "not found"**:
```python
# Good: Use 0 as sentinel value for "not found"
def get_content_hash(...) -> int:  # Returns 0 if not found
    ...
    if row and row[0] is not None:
        return cast(int, row[0])
    return 0

# Caller checks for 0
if content_hash == 0:
    raise_validation_error("Revision not found", status_code=404)
```

#### Exception Handling in Tests
```python
# raise_validation_error always raises HTTPException
from fastapi import HTTPException
with pytest.raises(HTTPException, match=".*"):
    repository.some_method(invalid_data)

# Other ValueErrors (not from raise_validation_error) should be caught by linters
# Code should not raise ValueError directly - use raise_validation_error() instead
```

### Code Structure

#### FastAPI Applications
```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

@asynccontextmanager
async def lifespan(app_: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown tasks."""
    # Startup code
    yield
    # Shutdown code

app = FastAPI(
    lifespan=lifespan,
    response_model_by_alias=True,  # Required: use field aliases in JSON responses
)
```

**Important:** Always include `response_model_by_alias=True` when creating FastAPI apps. This ensures Pydantic model field aliases (e.g., `@id`, `@type`) are used in serialized JSON responses instead of Python attribute names.

#### Pydantic Models
```python
from pydantic import BaseModel, Field

class EntityJsonImportRequest(BaseModel):
    """Request model for JSON import operations."""

    model_config = {"extra": "forbid"}  # No extra fields allowed

    entities: List[Dict[str, Any]] = Field(..., description="List of entities to import")
    batch_size: int = Field(default=100, ge=1, le=1000)
```

#### Logging
```python
import logging

logger = logging.getLogger(__name__)

# Use appropriate log levels
logger.debug("Initializing clients...")
logger.info("Processing entity data")
logger.warning("Potential issue detected")
logger.error("Failed to process entity")
```

### Testing Patterns

#### Unit Tests
```python
import pytest
from models.json_parser.entity_parser import parse_entity_data

def test_parse_string_value():
    """Test that string values are parsed correctly."""
    datavalue = {"value": "test string"}

    result = parse_string_value(datavalue)

    assert result.value == "test string"
    assert isinstance(result, StringValue)
```

#### Integration Tests

Integration tests should use `httpx.AsyncClient` with `ASGITransport` for FastAPI app testing:

```python
import pytest
from httpx import ASGITransport, AsyncClient

@pytest.mark.asyncio
@pytest.mark.integration
async def test_api_endpoint() -> None:
    """Example integration test using ASGITransport."""
    from models.rest_api.main import app
    
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/v1/entitybase/endpoint",
            json={"data": "value"},
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        assert response.status_code == 200
```

**Key Points:**
- Always use `@pytest.mark.asyncio` decorator
- Import `app` inline within test function: `from models.rest_api.main import app`
- Use `/v1/entitybase/` prefix for all API endpoints
- Use `await` with all HTTP methods
- No external server required (faster test execution)

**URL Prefix Rules:**
- ✅ Correct: `/v1/entitybase/users/12345/watchlist`
- ❌ Incorrect: `/entitybase/v1/users/12345/watchlist`
- Health check uses: `/health` (no prefix)

**Migration Complete:**
All 16 `requests.Session` test files have been migrated to `ASGITransport`:
- test_item_terms.py (21 tests)
- test_entity_basic.py (6 tests)
- test_entity_deletion.py
- test_entity_protection.py
- test_entities_list.py
- test_entity_other.py
- test_entity_status.py
- test_entity_schema_validation.py
- test_entity_revision_retrieval.py
- test_entity_revision_s3_storage.py
- test_entity_queries.py
- test_property_terms.py
- test_statement_basic.py (3 tests)
- test_statement_batch_and_properties.py
- test_statement_update.py
- test_entitybase_properties.py (3 tests)

```

#### Fixtures and Test Data
```python
@pytest.fixture
def sample_entity_data():
    """Provide sample entity data for testing."""
    return {
        "type": "item",
        "id": "Q1",
        "labels": {"en": {"language": "en", "value": "Universe"}}
    }

def test_entity_parsing(sample_entity_data):
    """Test entity parsing with sample data."""
    result = parse_entity_data(sample_entity_data)
    assert result.id == "Q1"
```

### File Organization

#### Source Code (`src/`)
```
src/
├── models/
│   ├── config/           # Configuration and settings
│   ├── data/            # Data models and schemas
│   ├── internal_representation/  # Core business logic
│   ├── json_parser/     # JSON parsing logic
│   └── rest_api/        # REST API endpoints and handlers
```

#### Tests (`tests/`)
```
tests/
├── unit/               # Unit tests
├── integration/        # Integration tests
│   └── models/
│       └── rest_api/   # API integration tests
└── e2e/               # End-to-end tests
```

### Performance Considerations

#### Code Complexity
- Keep cyclomatic complexity low (aim for < 10)
- Use radon to check complexity: `./run-radon.sh`

#### Memory Management
- Be mindful of large data structures
- Use streaming for large file processing
- Consider async/await for I/O operations

### Security Best Practices

#### Input Validation
- Always validate user inputs using Pydantic models
- Use `model_config = {"extra": "forbid"}` to prevent extra fields
- Sanitize data before processing

#### Secrets Management
- Never commit secrets or credentials
- Use environment variables for sensitive configuration
- Follow AWS IAM best practices for S3 access

#### Logging Security
- Don't log sensitive information (passwords, tokens, etc.)
- Use appropriate log levels to avoid exposing internal details

### Git Workflow

#### Commit Messages
- Use clear, descriptive commit messages
- Focus on "why" rather than "what"
- Example: "Add validation for entity ID format in import endpoint"

#### Branching
- Use feature branches for new work
- Keep commits focused and atomic
- Run full test suite before merging

### Development Environment

#### Docker Development
```bash
# Build and run development environment
./run-docker-build-tests.sh

# Clean rebuild (removes volumes)
./run-docker-build-tests.sh  # With volume pruning
```

#### Local Development
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
poetry install --with dev

Tell the user to start the API webserver if needed.
```
