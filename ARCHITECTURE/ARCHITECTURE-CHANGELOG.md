# Architecture Changelog

This file tracks architectural changes, feature additions, and modifications to the wikibase-backend system.

## [2025-12-27] Raw Revision Endpoint

### Summary

Added new endpoint to retrieve raw S3 entity data for specific entity revisions without API transformation.

### Motivation

Enable direct access to stored entity data for debugging, verification, and data integrity checks without needing external S3 inspection tools.

### Changes

#### New Models

**File: `src/services/shared/models/entity.py`**

Added two new Pydantic models for error handling:

```python
class RawRevisionErrorType(str, Enum):
    """Enum for raw revision endpoint error types"""
    ENTITY_NOT_FOUND = "entity_not_found"
    NO_REVISIONS = "no_revisions"
    REVISION_NOT_FOUND = "revision_not_found"


class RawRevisionErrorResponse(BaseModel):
    """Error response for raw revision endpoint"""
    detail: str = Field(description="Human-readable error message")
    error_type: RawRevisionErrorType = Field(description="Machine-readable error type")
```

**Rationale:**
- Enum ensures only valid error types can be used
- Type safety prevents typos in error_type values
- Clear documentation of all possible error scenarios
- Extensible for future error types

#### New API Endpoint

**File: `src/services/entity_api/main.py`**

Added endpoint: `GET /raw/{entity_id}/{revision_id}`

**Behavior:**
- Returns pure raw S3 entity data (no wrapper, no transformation)
- Validates entity exists in ID mapping
- Validates entity has revisions
- Validates requested revision exists for entity
- Returns detailed 404 errors for all failure scenarios

**Request Parameters:**
- `entity_id`: str - External entity identifier (e.g., "Q12345")
- `revision_id`: int - Specific revision number to retrieve

**Response (Success - 200):**
```json
{
  "id": "Q12345",
  "type": "item",
  "labels": {
    "en": {
      "language": "en",
      "value": "My Entity"
    }
  }
}
```

**Response (Error - 404):**

Scenario: Entity not found in ID mapping
```json
{
  "detail": "Entity Q99999 not found in ID mapping",
  "error_type": "entity_not_found"
}
```

Scenario: Entity exists but has no revisions
```json
{
  "detail": "Entity Q12345 has no revisions",
  "error_type": "no_revisions"
}
```

Scenario: Entity has revisions but requested revision doesn't exist
```json
{
  "detail": "Revision 5 not found for entity Q12345. Available revisions: [1, 2]",
  "error_type": "revision_not_found"
}
```

**Implementation Details:**
- Reuses existing `VitessClient.resolve_id()` to check entity existence
- Reuses existing `VitessClient.get_history()` to validate revision
- Reuses existing `S3Client.read_snapshot()` to read raw data
- Returns raw data via `snapshot.data` (no transformation)
- No additional logging (minimal approach)
- No rate limiting (production-ready)

### Error Type Enum

| Enum Value | When Used | HTTP Status |
|-------------|-------------|---------------|
| `ENTITY_NOT_FOUND` | Entity ID not found in mapping table | 404 |
| `NO_REVISIONS` | Entity exists but has no revisions | 404 |
| `REVISION_NOT_FOUND` | Requested revision doesn't exist | 404 |

### Testing

**Manual Testing Commands:**

1. Retrieve existing revision (success):
```bash
curl http://localhost:8000/raw/Q12345/1
```

2. Non-existent entity (entity_not_found):
```bash
curl http://localhost:8000/raw/Q99999/1
```

3. Entity with no revisions (no_revisions):
```bash
# Requires manually removing revisions or testing new entity
curl http://localhost:8000/raw/Q12345/1
```

4. Non-existent revision (revision_not_found):
```bash
# After creating revisions 1 and 2
curl http://localhost:8000/raw/Q12345/5
```

5. Compare with main endpoint (verify data integrity):
```bash
curl http://localhost:8000/entity/Q12345
curl http://localhost:8000/raw/Q12345/1
# Verify: raw response matches entity response's data field exactly
```

### Backward Compatibility

- ✅ No changes to existing endpoints
- ✅ No changes to existing models
- ✅ No database schema changes
- ✅ No S3 storage changes
- ✅ No changes to existing client methods

### Performance Considerations

- Uses existing VitessClient and S3Client methods
- Same performance characteristics as `GET /entity/{entity_id}`
- No additional computational overhead
- No additional I/O beyond standard entity retrieval

### Security Considerations

- Accessible in all environments (dev, staging, production)
- No authentication required (consistent with main API)
- No rate limiting (consistent with main API)
- Returns same data as existing endpoints (just in raw form)

### Future Enhancements

Potential improvements not included in this implementation:

1. Add authentication/authorization for raw endpoint
2. Add rate limiting for debug endpoints
3. Include debug metadata (S3 key path, content size, retrieval timing)
4. Add query parameters for format selection (raw vs. wrapped)
5. Add bulk raw revision retrieval endpoint
6. Include validation status in raw response

### Related Documentation

- [ARCHITECTURE/STORAGE-ARCHITECTURE.md](./ARCHITECTURE/STORAGE-ARCHITECTURE.md) - S3 and Vitess storage design
- [ARCHITECTURE/ENTITY-MODEL.md](./ARCHITECTURE/ENTITY-MODEL.md) - Hybrid ID strategy
- [src/schemas/s3-revision/1.0.0/schema.json](../src/schemas/s3-revision/1.0.0/schema.json) - Entity schema definition
