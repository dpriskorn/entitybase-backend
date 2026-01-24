# Agent Instructions for Wikibase Backend

This document provides guidelines and commands for agentic coding assistants working on the Wikibase Backend project.

## Build/Lint/Test Commands

### Running Tests

#### All Tests
```bash
# Run unit tests only
./run-unit-tests.sh

# Run all tests (unit + integration) with coverage
./run-coverage.sh
```

#### Single Test File
```bash
# Run a specific test file
source .venv/bin/activate
export PYTHONPATH=src
pytest tests/path/to/test_file.py -v

# Example: Run a specific test file
pytest tests/test_lexeme_processing.py -v
```

#### Single Test Function/Method
```bash
# Run a specific test function
source .venv/bin/activate
export PYTHONPATH=src
pytest tests/path/to/test_file.py::TestClass::test_method -v

# Run a specific test function (standalone function)
pytest tests/test_lexeme_processing.py::test_lexeme_l42_processing -v
```

#### Test Categories
```bash
# Unit tests only
pytest -m unit -n auto
```

### Linting and Code Quality

#### All Linters
```bash
./run-linters.sh
```

#### Individual Linters
```bash
# Ruff (linting and formatting)
./run-ruff.sh

# MyPy (type checking)
./run-mypy.sh

# Radon (complexity analysis)
./run-radon.sh

# Vulture (dead code detection)
./run-vulture.sh
```

#### Custom Linters
```bash
# Various custom linters for specific patterns
./run-str-lint.sh
./run-int-lint.sh
./run-response-model-lint.sh
./run-logger-lint.sh
./run-pydantic-field-lint.sh
./run-tuple-lint.sh
./run-init-lint.sh
./run-any-lint.sh
./run-cast-lint.sh
./run-key-length-lint.sh
./run-backslash-lint.sh
./run-json-lint.sh
```


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

#### Exception Handling in Tests
```python
# Tests should expect ValueError in test environments
with pytest.raises(ValueError):
    repository.some_method(invalid_data)
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

app = FastAPI(lifespan=lifespan)
```

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
```python
import pytest
from httpx import AsyncClient

class TestJsonImportIntegration:
    """Integration tests for the /json-import endpoint."""

    @pytest.fixture
    async def client(self, app):
        """Create test client for the FastAPI app."""
        async with AsyncClient(app=app, base_url="http://testserver") as client:
            yield client

    async def test_json_import_endpoint_exists(self, client):
        """Test that the JSON import endpoint exists."""
        response = await client.get("/v1/json-import")
        assert response.status_code in [200, 405]  # Exists or method not allowed
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
./run-docker-build.sh

# Clean rebuild (removes volumes)
./run-docker-build.sh  # With volume pruning
```

#### Local Development
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
poetry install --with dev

# Run development server
uvicorn src.models.rest_api.main:app --reload
```
