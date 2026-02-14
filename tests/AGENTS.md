Test Structure Analysis
1. Test Frameworks and Patterns
Primary Test Framework:
- pytest with pytest-asyncio for async support
- pytest-xdist for parallel execution
- pytest-mock for mocking
- pytest-cov for coverage reporting
Test Organization:
- Three distinct test categories with pytest markers:
  - @pytest.mark.unit - Unit tests
  - @pytest.mark.integration - Integration tests
  - @pytest.mark.e2e - End-to-end tests
- Directory hierarchy mirrors src/models/ structure (see Section 4)
Test Patterns:
- Unit tests: Use mocks (unittest.mock, pytest-mock) for all external dependencies
- Integration tests: Use ASGITransport with FastAPI app for API endpoint testing
- E2E tests: Use ASGITransport with FastAPI app for end-to-end workflow testing
2. Test Coverage Analysis
Current Coverage Threshold:
- Target: 50% minimum coverage
- Reports generated in XML and HTML formats
- Coverage reports generated for src/ directory only
Coverage Areas:
- Well covered: JSON parsers (value parsers, entity parsers, statement parsers)
- Moderately covered: Internal representation models, RDF builders
- Less covered: API handlers, services, repositories
- Minimal coverage: Configuration, infrastructure, error handling

3. Test Structure Breakdown
Test Files by Type:
Unit Tests (Primary Focus):
├── JSON Parsers (~20 test files)
│   ├── Value parsers (15+ tests)
│   ├── Entity parsers
│   ├── Property parsers
│   └── Statement parsers
├── Internal Representation (~15 test files)
│   ├── Value models (10+ tests)
│   ├── Entity models
│   ├── Statement models
│   └── Utility classes
├── RDF Builders (~5 test files)
├── Validation (~2 test files)
└── Services (~1 test file)
Integration Tests (~15 test files):
├── REST API endpoints (ASGITransport)
├── Database repositories (Vitess)
├── S3 storage
├── Worker processes
└── Infrastructure components
E2E Tests (~4 test files):
├── Entity lifecycle workflows
├── User workflows
└── Endorsements

Directory Hierarchy:
- tests/unit/models/ mirrors src/models/ structure
- tests/integration/models/ mirrors src/models/ structure
- tests/e2e/models/ mirrors src/models/ structure
- Each subdirectory in src/models/ has corresponding test directories
- See Section 4 for detailed hierarchy guidelines

4. Directory Hierarchy Guidelines

Test directories must mirror the source code structure in `src/models/`:

```
src/models/
├── config/
├── data/
│   ├── infrastructure/
│   └── rest_api/
├── internal_representation/
├── json_parser/
├── rdf_builder/
├── rest_api/
├── services/
├── validation/
└── workers/

tests/unit/models/
├── config/                    # Tests for models/config/
├── data/                     # Tests for models/data/
├── internal_representation/  # Tests for models/internal_representation/
├── json_parser/              # Tests for models/json_parser/
├── rdf_builder/              # Tests for models/rdf_builder/
├── rest_api/                 # Tests for models/rest_api/
├── services/                 # Tests for models/services/
├── validation/               # Tests for models/validation/
└── workers/                  # Tests for models/workers/

tests/integration/models/
├── infrastructure/           # Integration tests for infrastructure
├── rest_api/                 # Integration tests for API endpoints
└── workers/                  # Integration tests for workers

tests/e2e/models/
├── infrastructure/           # E2E tests for infrastructure
├── internal_representation/  # E2E tests for business logic
└── rest_api/                 # E2E workflow tests
```

**Key Principles:**
- Each subdirectory in `src/models/` should have corresponding test directories in `tests/unit/models/`
- Maintain consistent naming and organization across test types
- Unit tests in `tests/unit/models/` use mocks for external dependencies
- Integration tests in `tests/integration/models/` use ASGITransport for API endpoints
- E2E tests in `tests/e2e/models/` use ASGITransport for workflow testing

5. Test Configuration & Infrastructure
Current Setup:
- Separate conftest.py files for unit, integration, and e2e tests
- Mock fixtures for external dependencies in unit tests
- ASGITransport fixtures for integration and e2e tests
- pytest-asyncio for async test support

Key Fixtures:
- `tests/conftest.py` - Global test configuration
- `tests/unit/conftest.py` - Unit test fixtures and mocks
- `tests/integration/conftest.py` - Integration test fixtures with ASGITransport
- `tests/e2e/conftest.py` - E2E test fixtures with ASGITransport

6. Test Documentation
Current State:
- Basic pytest configuration in pyproject.toml
- Some inline documentation in test files
- Agent instructions document provides testing guidelines

Best Practices:
- Maintain directory hierarchy mirroring src/models/
- Use descriptive test names and docstrings
- Add docstrings to test functions explaining what is being tested
- Include inline comments for complex test scenarios
- Document mock usage patterns in test files

This document provides a comprehensive overview of the test suite structure and testing patterns for the Wikibase Backend project.

7. Hash Resolution in Tests

The API uses content hashes (integers) to reference labels, descriptions, aliases,
statements, sitelinks, qualifiers, references, snaks, glosses, and representations.

- **Entity IDs** (e.g., `Q123`, `P456`) are range-based, not hashes
- **POST/PUT/PATCH/DELETE endpoints**: Responses contain content hashes (integers)
- **GET endpoints**: Send hashes to retrieve resolved content

**Schema Reference:** [`schemas/entitybase/entity/2.0.0/schema.yaml`](../schemas/entitybase/entity/2.0.0/schema.yaml)

**Example - Creating an entity and resolving hashes:**
```python
@pytest.mark.asyncio
async def test_hash_resolution() -> None:
    from models.rest_api.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # POST returns entity with hash references
        response = await client.post(
            "/v1/entitybase/entities/items",
            json={"type": "item", "labels": {"en": {"value": "Test"}}},
            headers={"X-Edit-Summary": "test", "X-User-ID": "0"},
        )
        entity = response.json()
        entity_id = entity["id"]  # Range-based ID like "Q123"
        label_hash = entity["data"]["labels"]["en"]  # Integer hash like 123456789
        statement_hashes = entity["data"]["statements"]["hashes"]  # Array of integers

        # GET resolves label hash to actual text
        response = await client.get(f"/v1/entitybase/entities/labels/{label_hash}")
        label = response.json()  # {"language": "en", "value": "Test"}

        # GET resolves statement hash to full statement content
        if statement_hashes:
            response = await client.get(
                f"/v1/entitybase/statements/{statement_hashes[0]}"
            )
            statement = response.json()  # Full statement data
```

8. Status Code Assertions

When testing API responses, assertions MUST check for a single expected status code,
not multiple alternatives.

**Incorrect (not allowed):**
```python
# Do NOT use this pattern
assert response.status_code in [200, 201]
assert response.status_code in (200, 201, 204)
```

**Correct:**
```python
# Always assert exactly one expected status code
assert response.status_code == 201
```

**Rationale:**
- Tests should verify a specific expected outcome
- Multiple status codes in assertions mask which behavior actually occurred
- Makes debugging harder when tests fail
- Each test case should have a single, deterministic expectation

If you need to test that an endpoint accepts multiple valid inputs with different outcomes,
write separate test functions for each case.