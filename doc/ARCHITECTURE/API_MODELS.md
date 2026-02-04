# API Models Overview

This document describes all Pydantic models used for REST API requests and responses in the Wikibase backend.

## Entity Response Models

### src/models/data/rest_api/v1/entitybase/response/entity/entitybase.py

#### EntityLabelsResponse
Collection of labels keyed by language code.

**Fields**:
- `data` (dict[str, LabelValue]): Dictionary of labels keyed by language code. Example: {'en': {'language': 'en', 'value': 'Test'}}.

**Methods**:
- `__getitem__(key: str)`: Get label by key
- `get(language_code: str)`: Get label for specified language code

#### EntityDescriptionsResponse
Collection of descriptions keyed by language code.

**Fields**:
- `data` (dict[str, DescriptionValue]): Dictionary of descriptions keyed by language code. Example: {'en': {'language': 'en', 'value': 'A test description'}}.

**Methods**:
- `__getitem__(key: str)`: Get description by key
- `get(language_code: str)`: Get description for specified language code

#### EntityAliasesResponse
Collection of aliases keyed by language code.

**Fields**:
- `data` (dict[str, list[AliasValue]]): Dictionary of aliases keyed by language code.

**Methods**:
- `__getitem__(key: str)`: Get aliases by key
- `get(language_code: str)`: Get aliases for specified language code

#### EntityStatementsResponse
List of entity statements.

**Fields**:
- `data` (list[dict[str, Any]]): List of entity statements.

#### EntitySitelinksResponse
Collection of sitelinks.

**Fields**:
- `data` (dict[str, SitelinkValue]): Dictionary of sitelinks keyed by site.

**Methods**:
- `__getitem__(key: str)`: Get sitelink by key
- `get(site: str)`: Get sitelink for specified site

#### EntityHistoryEntry
Response model for a single entity history entry.

**Fields**:
- `revision_id` (int): Revision ID. Example: 12345.
- `created_at` (str): Creation timestamp (ISO format). Example: '2023-01-01T12:00:00Z'.
- `user_id` (int): User ID who made the change. Example: 67890.
- `summary` (str): Edit summary text. Example: 'Added label'.

#### EntityResponse
Response model for entity data.

**Fields**:
- `id` (str): Entity ID. Example: 'Q42'.
- `rev_id` (int, alias): Revision ID of entity. Example: 12345.
- `data` (S3RevisionData, alias): Full entity JSON data. Example: {'id': 'Q42', 'type': 'item'}.
- `state` (EntityState | None): Entity state information (optional, may be None for revisions).

#### EntityDeleteResponse
Response model for entity deletion.

**Fields**:
- `id` (str): Entity ID. Example: 'Q42'.
- `rev_id` (int, alias): Revision ID at deletion. Example: 12345.
- `is_deleted` (bool): Whether entity is deleted. Example: true.
- `del_type` (str, alias): Type of deletion performed. Example: 'soft_delete'.
- `del_status` (str, alias): Status of deletion (soft_deleted/hard_deleted). Example: 'soft_deleted'.

#### EntityRedirectResponse
Response model for entity redirect creation.

**Fields**:
- `redirect_from_id` (str): Entity ID being redirected from
- `redirect_to_id` (str): Entity ID being redirected to
- `created_at` (str): Creation timestamp of redirect
- `revision_id` (int): Revision ID of redirect

#### EntityListResponse
Response model for entity list queries.

**Fields**:
- `entities` (list[dict[str, Any]]): List of entities with their metadata
- `count` (int): Total number of entities returned

#### EntityMetadataResponse
Model for entity metadata.

**Fields**:
- `id` (str): Entity ID
- `type` (str, default="item"): Entity type
- `labels` (EntityLabelsResponse): Entity labels
- `descriptions` (EntityDescriptionsResponse): Entity descriptions
- `aliases` (EntityAliasesResponse): Entity aliases
- `statements` (EntityStatementsResponse): Entity statements
- `sitelinks` (EntitySitelinksResponse): Entity sitelinks

#### EntityMetadataBatchResponse
Response model for batch entity metadata fetching.

**Fields**:
- `metadata` (dict[str, EntityMetadataResponse | None]): Dictionary mapping entity_id to metadata or None

#### ProtectionResponse
Model for entity protection information.

**Fields**:
- `semi_prot` (bool, alias): Whether entity is semi-protected. Example: true.
- `locked` (bool, alias): Whether entity is locked. Example: false.
- `archived` (bool, alias): Whether entity is archived. Example: false.
- `dangling` (bool, alias): Whether entity is dangling. Example: false.
- `mass_edit` (bool, alias): Whether entity is mass edit protected. Example: true.

#### EntityJsonImportResponse
Response model for JSONL entity import operations.

**Fields**:
- `processed_count` (int): Number of lines processed
- `imported_count` (int): Number of entities successfully imported
- `failed_count` (int): Number of entities that failed to import
- `error_log_path` (str): Path to error log file for malformed lines

---

## General Response Models

### src/models/data/rest_api/v1/entitybase/response/health.py

#### HealthResponse
Response model for health check.

**Fields**:
- `status` (str): Health status

#### HealthCheckResponse
Detailed response model for health check.

**Fields**:
- `status` (str): Overall health status
- `s3` (str): S3 service health status. Example: 'healthy'.
- `vitess` (str): Vitess service health status. Example: 'healthy'.
- `timestamp` (str): Timestamp of health check

#### WorkerHealthCheckResponse
Model for worker health check response.

**Fields**:
- `status` (str): Health status: healthy or unhealthy
- `worker_id` (str): Unique worker identifier
- `range_status` (dict[str, Any]): Current ID range allocation status

---

## Entity Response Models (Additional)

### src/models/data/rest_api/v1/entitybase/response/entity/

#### BacklinkStatisticsResponse
Response model for entity backlink statistics.

#### ChangeResponse
Response model for entity change operations.

#### RevertResponse
Response model for entity revert operations.

#### BacklinksResponse
Response model for entity backlinks list.

#### WikibaseResponse
Response model for Wikibase-specific data.

#### RevisionReadResponse
Response model for revision data retrieval.

---

## User Response Models

### src/models/data/rest_api/v1/entitybase/response/user.py

User-related response models for user information, activity, preferences, and statistics.

### src/models/data/rest_api/v1/entitybase/response/user_activity.py

Response models for user activity tracking and history.

### src/models/data/rest_api/v1/entitybase/response/user_stats.py

Response models for user statistics and metrics.

### src/models/data/rest_api/v1/entitybase/response/user_preferences.py

Response models for user preferences and settings.

---

## Social Features Response Models

### src/models/data/rest_api/v1/entitybase/response/thanks.py

Response models for thanks feature.

### src/models/data/rest_api/v1/entitybase/response/endorsements.py

Response models for statement endorsements.

### src/models/data/rest_api/v1/entitybase/response/watchlist.py

Response models for watchlist management and notifications.

---

## Other Response Models

### src/models/data/rest_api/v1/entitybase/response/id_response.py

Response models for entity ID operations.

### src/models/data/rest_api/v1/entitybase/response/result.py

Generic result and response wrapper models.

### src/models/data/rest_api/v1/entitybase/response/listings.py

Response models for entity listings and pagination.

### src/models/data/rest_api/v1/entitybase/response/events.py

Response models for event streaming and change notifications.

### src/models/data/rest_api/v1/entitybase/response/rdf.py

Response models for RDF export operations.

### src/models/data/rest_api/v1/entitybase/response/lexemes.py

Response models for lexeme-specific operations.

---

## Common Response Patterns

### Error Handling
All response models use Pydantic for validation and support:
- Field validation with descriptions
- Alias support for field naming
- Default values where applicable
- Custom error handling via `raise_validation_error()`

### DateTime Formatting
All timestamp fields use ISO 8601 format:
- Example: `2023-01-01T12:00:00Z`

### Entity ID Format
Entity IDs follow Wikibase conventions:
- Items: `Q123`
- Properties: `P42`
- Lexemes: `L999`
- Entity Schemas: `E100`

---

## Related Documentation

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Overall system architecture
- [SERVICES.md](./SERVICES.md) - Service layer architecture
- [src/models/rest_api/ENDPOINTS.md](../../src/models/rest_api/ENDPOINTS.md) - REST API endpoints
