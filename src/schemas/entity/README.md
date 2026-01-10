# Entity API Response Schema

JSON Schema for EntityBase JSON Entity v1 API responses.

## Versioning

Follows semantic versioning: `MAJOR.MINOR.PATCH`

- MAJOR: Breaking changes
- MINOR: Backward-compatible additions
- PATCH: Backward-compatible bug fixes

## Schema Files

- `1.0.0/schema.json` - Initial unified entity response schema
- `latest/` - Symlink to latest version

## Coverage

Validates responses from:
- `GET /entities/{entity_id}`
- `GET /item/{entity_id}`
- `GET /property/{entity_id}`
- `GET /lexeme/{entity_id}`

## Usage

```python
import json
from jsonschema import validate

# Load schema
with open('src/schemas/entity/latest/schema.json') as f:
    schema = json.load(f)

# Validate response
validate(instance=api_response, schema=schema)
```