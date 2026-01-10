# Architecture Changelog

This file tracks architectural changes, feature additions, and modifications to wikibase-backend system.

## [2026-01-10] Backlinks Support Implementation

### Summary

Added `entity_backlinks` table to track incoming references between entities, enabling efficient backlink queries. Implemented QID extraction from statement JSON to identify referenced entities in mainsnak, qualifiers, and references.

### Motivation

- **Query Efficiency**: Enable fast lookup of entities that reference a given entity in their statements
- **Scalability**: Use BIGINT internal_ids for FKs, with sharding on referenced_internal_id
- **Completeness**: Support full Wikibase backlinks functionality for entity relationships

### Changes

#### New entity_backlinks Table

**File**: `src/models/infrastructure/vitess/schema.py`

Added table to track backlinks with composite primary key for uniqueness:

- `referenced_internal_id` BIGINT (entity being referenced)
- `referencing_internal_id` BIGINT (entity making the reference)
- `statement_hash` BIGINT (links to specific statement)
- `property_id` VARCHAR(32) (property used in statement)
- `rank` ENUM (preferred/normal/deprecated)

Includes foreign key constraints and indexes for query performance.

#### QID Extraction Logic

**File**: `src/models/domain/entity/statement_parser.py` (new)

Recursive function to extract entity IDs from statement JSON structures.

#### Updated Entity Write Logic

**File**: `src/models/rest_api/handlers/entity/types.py`

Modified entity update/create to populate backlinks table during statement processing.

#### New API Endpoint

**File**: `src/models/rest_api/handlers/entity/backlinks.py` (new)

`GET /entities/{id}/backlinks` returns paginated list of referencing entities.

## [2026-01-09] Transaction-Based Item Creation with Rollback

### Summary

Implemented atomic item creation using a Pydantic `CreationTransaction` class that manages operations with full rollback on failure. Includes per-statement rollback, worker handshake for ID confirmation, and removal of redundant checks. Updated enumeration handlers with high minimum IDs to avoid Wikidata collisions.

### Motivation

- **Atomicity**: Ensure creation is all-or-nothing; rollback on S3/Vitess failures prevents orphaned data.
- **Reliability**: Trust worker for unique IDs, but confirm usage; rollback statements individually.
- **Simplicity**: Remove existence/deletion checks; direct revision ID = 1 for creations.
- **Collision Avoidance**: Set minimum IDs above Wikidata ranges (Q: 300M, P: 30K, L: 5M, E: 50K).

### Changes

#### New CreationTransaction Class

**File**: `src/models/rest_api/handlers/entity/creation_transaction.py`

Pydantic BaseModel for managing creation operations:

- `register_entity()`: Reserves ID in Vitess.
- `process_statements()`: Hashes/deduplicates statements, stores in S3/Vitess.
- `create_revision()`: Stores revision snapshot with CAS protection against concurrent modifications.
- `publish_event()`: Emits change event.
- `commit()`: Confirms ID usage; clears rollback operations.
- `rollback()`: Undoes all operations in reverse (deletes from Vitess/S3, decrements ref_counts).

**Features**:
- Per-statement rollback: Tracks hashes, decrements ref_counts, deletes orphaned S3 objects.
- Logging: Info logs at method starts for tracing.
- Reusable: Designed for future extension to updates/deletes.

#### Updated Item Creation Flow

**File**: `src/models/rest_api/handlers/entity/types.py`

- Removed existence/deletion checks (trust worker).
- Removed idempotency check (no prior revisions).
- Direct `new_revision_id = 1` for creations.
- Wrapped operations in `CreationTransaction` with try/except rollback.

#### Enumeration Handler Updates

**Files**: `src/models/rest_api/handlers/entity/enumeration/*.py`

- Moved classes to individual files with high minimum IDs.
- Updated base classes: `min_id` set to avoid Wikidata collisions.

#### Documentation Updates

**File**: `doc/ARCHITECTURE/ENTITY-MODEL.md`

- Updated entity creation flow diagram to reflect transaction-based approach.
- Emphasized rollback and worker handshake.

### Impact

- **Reliability**: Atomic creation with full rollback; no orphaned data.
- **Performance**: Removed unnecessary checks; faster for new items.
- **ID Safety**: Minimum IDs prevent Wikidata conflicts.
- **Maintainability**: Transaction class encapsulates rollback logic.

### Backward Compatibility

- **Non-breaking**: API unchanged; internal flow improved.
- **Rollbacks**: Graceful failure handling; logs warnings on rollback errors.

---

## [2026-01-09] Enumeration Handler Updates and Documentation Refinements

### Summary

Updated enumeration handlers with correct minimum ID values to prevent collisions with Wikidata.org entities, refined S3 storage paths by removing the "r" prefix for consistency, and updated documentation to reflect 1-based revision indexing. Bumped S3 revision schema to v1.2.0 for documentation alignment.

### Motivation

- **Collision Prevention**: Ensure new entity IDs start above existing Wikidata ranges to avoid conflicts during migration or coexistence.
- **Path Consistency**: Standardize S3 object paths to use clean integer revision IDs without prefixes.
- **Documentation Accuracy**: Align docs with 1-based revision indexing and updated minimum ID values.

### Changes

#### Updated Enumeration Handlers

**Files**: `src/models/rest_api/handlers/entity/enumeration/*.py`

Updated minimum ID values in base handler classes to safe ranges above Wikidata maximums:

- Item: `min_id = 300_000_000` (above Q120M+)
- Property: `min_id = 30_000` (above P10K+)
- Lexeme: `min_id = 5_000_000` (above L1M+)
- EntitySchema: `min_id = 50_000` (conservative buffer)

**Rationale**:
- Prevents ID collisions when integrating with or migrating from Wikidata.
- Values set conservatively above current Wikidata ranges with buffers for growth.

#### S3 Path Standardization

**Files**: Documentation files (`doc/ARCHITECTURE/ENTITY-MODEL.md`, etc.)

Removed "r" prefix from S3 revision paths:
- Before: `s3://wikibase-revisions/Q123/r42.json`
- After: `s3://wikibase-revisions/Q123/42.json`

**Rationale**:
- Simplifies paths to use raw integer revision IDs.
- Consistent with schema expectations of integer revision identifiers.



**Rationale**:
- Marks documentation refinements and minimum ID awareness.
- No breaking changes to JSON structure.

#### Documentation Updates

**File**: `doc/ARCHITECTURE/ENTITY-MODEL.md`

- Updated entity creation examples to use revision_id=1 and clean S3 paths.
- Emphasized 1-based revision indexing.
- Added notes on minimum ID collision avoidance.

### Impact

- **ID Safety**: New entities use safe starting IDs preventing Wikidata conflicts.
- **Storage Consistency**: S3 paths use clean integer revision IDs.
- **Developer Experience**: Documentation accurately reflects implementation details.

### Backward Compatibility

- **Non-breaking**: Enumeration changes affect only new entity creation.
- **S3 Paths**: Existing paths remain functional; new paths follow updated convention.
- **Schema**: v1.2.0 compatible with v1.1.0 (no structural changes).

---

## [2026-01-08] Change Event Producer for Redpanda

### Summary

Added change event producer infrastructure for publishing entity change events to Redpanda (Kafka-compatible streaming platform). Implemented ChangeType enum with 10 change classifications and EntityChangeEvent BaseModel for structured event publishing. All entity operations (creation, edit, redirect, archival, lock, deletion) now emit change events to `wikibase.entity_change` topic for downstream consumers like RDF streamers and analytics pipelines.

### Motivation

Wikibase-backend requires change event streaming for:

- **Downstream consumers**: RDF change streamers, search indexers, analytics pipelines need real-time entity change notifications
- **Event-driven architecture**: Decouple entity operations from change processing, enable reactive updates
- **Change detection**: Continuous RDF Change Streamer needs entity change events to trigger RDF diff computation
- **Audit trail**: External systems can track all entity modifications with proper change type classification
- **Scalability**: Async event production allows API to remain responsive while events are processed asynchronously

### Changes

#### New Kafka Configuration

**File**: `src/models/config/settings.py`

```python
class Settings(BaseSettings):
    kafka_brokers: str = "redpanda:9092"
    kafka_topic: str = "wikibase.entity_change"
```

**Environment variables**:
- `KAFKA_BROKERS`: Redpanda broker address (default: `redpanda:9092`)
- `KAFKA_TOPIC`: Topic for entity change events (default: `wikibase.entity_change`)

**File**: `docker-compose.yml`

```yaml
redpanda:
  image: redpandadata/redpanda:latest
  ports:
    - "9092:9092"
  healthcheck:
    test: ["CMD-SHELL", "rpk cluster health | grep -q 'Healthy'"]

rest-api:
  environment:
    KAFKA_BROKERS: redpanda:9092
    KAFKA_TOPIC: wikibase.entity_change
  depends_on:
    redpanda:
      condition: service_healthy
```

#### New ChangeType Enum

**File**: `src/models/api_models.py`

```python
class ChangeType(str, Enum):
    """Change event types for streaming to Redpanda"""

    CREATION = "creation"
    EDIT = "edit"
    REDIRECT = "redirect"
    UNREDIRECT = "unredirect"
    ARCHIVAL = "archival"
    UNARCHIVAL = "unarchival"
    LOCK = "lock"
    UNLOCK = "unlock"
    SOFT_DELETE = "soft_delete"
    HARD_DELETE = "hard_delete"
```

**Rationale**:
- Underscore naming for consistency with Python conventions
- All 10 change types map directly to existing EditType classifications
- Single topic strategy simplifies consumer architecture

#### New Entity Change Event Model

**File**: `src/models/api_models.py`

```python
class EntityChangeEvent(BaseModel):
    """Entity change event for publishing to Redpanda"""

    entity_id: str = Field(..., description="Entity ID (e.g., Q42)")
    revision_id: int = Field(..., description="Revision ID of the change")
    change_type: ChangeType = Field(..., description="Type of change")
    from_revision_id: Optional[int] = Field(
        None, description="Previous revision ID (null for creation)"
    )
    changed_at: datetime = Field(..., description="Timestamp of change")
    editor: Optional[str] = Field(None, description="Editor who made the change")
    edit_summary: Optional[str] = Field(None, description="Edit summary")
    bot: bool = Field(False, description="Whether this was a bot edit")

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
```

**Event schema**:
```json
{
  "entity_id": "Q42",
  "revision_id": 101,
  "change_type": "edit",
  "from_revision_id": 100,
  "changed_at": "2026-01-08T12:00:00Z",
  "editor": "User:Example",
  "edit_summary": "Updated description",
  "bot": false
}
```

#### New Kafka Producer Client

**File**: `src/models/infrastructure/kafka/kafka_producer.py`

```python
from aiokafka import AIOKafkaProducer
from pydantic import BaseModel


class KafkaProducerClient(BaseModel):
    """Async Kafka producer client for publishing change events"""

    bootstrap_servers: str
    topic: str
    producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        """Start the Kafka producer"""

    async def stop(self) -> None:
        """Stop the Kafka producer"""

    async def publish_change(self, event: EntityChangeEvent) -> None:
        """Publish entity change event to Kafka"""

    async def publish_change_sync(self, event: EntityChangeEvent) -> None:
        """Synchronous publish with delivery confirmation"""
```

**Features**:
- Async production using `aiokafka` for non-blocking event publishing
- Automatic serialization to JSON
- Entity ID as message key for partition ordering
- Error handling with logging (no exceptions on publish failure)
- Start/stop lifecycle management

**Rationale**:
- Async production ensures API responses are not blocked
- Entity ID as key ensures all events for an entity go to same partition
- Graceful error handling prevents API failures from Kafka issues

#### New Kafka Infrastructure Module

**File**: `src/models/infrastructure/kafka/__init__.py`

```python
from models.infrastructure.kafka.kafka_producer import KafkaProducerClient

__all__ = ["KafkaProducerClient"]
```

**Rationale**:
- Clean module structure for Kafka infrastructure
- Follows existing pattern in `s3/` and `vitess/` modules

#### Updated Clients Class

**File**: `src/models/rest_api/clients.py`

```python
from models.infrastructure.kafka.kafka_producer import KafkaProducerClient


class Clients(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    s3: S3Client | None = None
    vitess: VitessClient | None = None
    property_registry: PropertyRegistry | None = None
    kafka_producer: KafkaProducerClient | None = None

    def __init__(
        self,
        s3: "S3Config",
        vitess: "VitessConfig",
        kafka_brokers: str | None = None,
        kafka_topic: str | None = None,
        property_registry_path: Path | None = None,
        **kwargs: str,
    ) -> None:
        super().__init__(
            s3=S3Client(config=s3),
            vitess=VitessClient(config=vitess),
            kafka_producer=KafkaProducerClient(
                bootstrap_servers=kafka_brokers,
                topic=kafka_topic,
            ) if kafka_brokers and kafka_topic else None,
            property_registry=(
                load_property_registry(property_registry_path)
                if property_registry_path
                else None
            ),
            **kwargs,
        )
```

#### Updated FastAPI Lifespan

**File**: `src/models/rest_api/main.py`

```python
@asynccontextmanager
async def lifespan(app_: FastAPI) -> AsyncGenerator[None, None]:
    try:
        logger.debug("Initializing clients...")
        s3_config = settings.to_s3_config()
        vitess_config = settings.to_vitess_config()
        kafka_brokers = settings.kafka_brokers
        kafka_topic = settings.kafka_topic

        logger.debug(f"Kafka config: brokers={kafka_brokers}, topic={kafka_topic}")

        app_.state.clients = Clients(
            s3=s3_config,
            vitess=vitess_config,
            kafka_brokers=kafka_brokers,
            kafka_topic=kafka_topic,
            property_registry_path=property_registry_path,
        )

        # Start Kafka producer
        if app_.state.clients.kafka_producer:
            await app_.state.clients.kafka_producer.start()
            logger.info("Kafka producer started")

        yield

        # Stop Kafka producer
        if app_.state.clients.kafka_producer:
            await app_.state.clients.kafka_producer.stop()
            logger.info("Kafka producer stopped")

    except Exception as e:
        logger.error(
            f"Failed to initialize clients: {type(e).__name__}: {e}", exc_info=True
        )
        raise
```

**Rationale**:
- Start producer during app startup, stop during shutdown
- Graceful handling of producer lifecycle
- No blocking during initialization

#### Change Type Mapping

**EditType → ChangeType mapping**:

| EditType | ChangeType |
|----------|------------|
| `MANUAL_CREATE` | `CREATION` |
| `MANUAL_UPDATE` | `EDIT` |
| `REDIRECT_CREATE` | `REDIRECT` |
| `REDIRECT_REVERT` | `UNREDIRECT` |
| `ARCHIVE_ADDED` | `ARCHIVAL` |
| `ARCHIVE_REMOVED` | `UNARCHIVAL` |
| `LOCK_ADDED` | `LOCK` |
| `LOCK_REMOVED` | `UNLOCK` |
| `SOFT_DELETE` | `SOFT_DELETE` |
| `HARD_DELETE` | `HARD_DELETE` |

**Rationale**:
- Clean separation between input classification and output events
- Consistent naming convention (underscores)
- Single source of truth for mapping logic

#### Entity Handler Integration

**File**: `src/models/rest_api/handlers/entity_handler.py`

```python
class EntityHandler:
    def create_entity(self, request, vitess, s3, validator):
        # ... existing logic ...

        # Publish change event
        if clients.kafka_producer:
            change_event = EntityChangeEvent(
                entity_id=entity_id,
                revision_id=new_revision_id,
                change_type=ChangeType.CREATION,
                from_revision_id=None,
                changed_at=datetime.utcnow(),
                editor=request.editor or None,
                edit_summary=request.edit_summary or None,
                bot=request.bot,
            )
            await clients.kafka_producer.publish_change(change_event)
```

**Integration points**:
- **Entity creation**: Emit `CREATION` event
- **Entity update**: Emit `EDIT` event with `from_revision_id`
- **Entity deletion**: Emit `SOFT_DELETE` or `HARD_DELETE` event
- **Redirect creation**: Emit `REDIRECT` event
- **Redirect reversion**: Emit `UNREDIRECT` event

**Rationale**:
- Async fire-and-forget publishing doesn't block API responses
- All change events include full context (editor, summary, bot flag)
- Optional producer check allows graceful degradation if Kafka unavailable

### Impact

- **API latency**: No measurable increase (async production, fire-and-forget)
- **Event coverage**: 100% of entity operations now emit change events
- **Downstream consumers**: RDF streamers, search indexers, analytics pipelines can consume real-time changes
- **Error handling**: Publish failures logged but don't affect entity operations
- **Scalability**: Partition by entity_id ensures ordering per entity

### Backward Compatibility

- **Non-breaking change**: Kafka producer initialization is optional
- **Existing consumers**: No changes required (new producer only adds functionality)
- **API contracts**: No changes to existing endpoints
- **Graceful degradation**: API works normally if Kafka is unavailable

### Future Enhancements

- Add change event schema registry for versioning
- Implement dead letter queue for failed events
- Add event batching for high-throughput scenarios
- Implement event replay capability for consumers
- Add change event metrics and monitoring

---

## [2026-01-07] Synchronous JSON Schema Validation

### Summary

Replaced background validation architecture with synchronous JSON schema validation at API layer. All incoming JSON requests are now validated against existing JSON schemas before persistence, ensuring data integrity and immediate error feedback.

### Motivation

- **Data integrity**: Catch schema violations at API boundary, prevent invalid data from entering system
- **Immediate feedback**: Users receive clear validation errors before data is stored
- **Simplification**: Removed need for background validation service, Kafka events, and cleanup jobs
- **Explicit contracts**: Existing JSON schemas document the expected data structure
- **Error reduction**: Prevent downstream failures in RDF conversion and other consumers

### Changes

#### Deprecated Background Validation Documentation

**Moved files to DEPRECATED/**:
- `doc/ARCHITECTURE/JSON-VALIDATION-STRATEGY.md` → `doc/ARCHITECTURE/DEPRECATED/JSON-VALIDATION-STRATEGY.md`
- `doc/ARCHITECTURE/POST-PROCESSING-VALIDATION.md` → `doc/ARCHITECTURE/DEPRECATED/POST-PROCESSING-VALIDATION.md`

Added deprecation notes explaining the architectural change from Option A (background validation) to synchronous validation.

#### New JSON Schema Validation Utility

**File**: `src/models/validation/json_schema_validator.py`

New validator using `jsonschema` Python library:

```python
class JsonSchemaValidator:
    def validate_entity_revision(self, data: dict) -> None
    def validate_statement(self, data: dict) -> None
```

Loads schemas from:
- `src/schemas/s3-revision/1.2.0/schema.json` - Entity revision structure
- `src/schemas/s3-statement/1.0.0/schema.json` - Statement structure

#### Updated Dependencies

**File**: `pyproject.toml`

Added dependency:
```toml
"jsonschema (>=4.23.0,<5.0.0)"
```

#### API Endpoint Validation

**File**: `src/models/entity_api/main.py`

Added JSON schema validation to POST endpoints:

1. **POST /entity** - Validate EntityCreateRequest.data against s3-revision schema
2. **POST /redirects** - Validate redirect request structure
3. **POST /entities/{entity_id}/revert-redirect** - Validate revert request
4. **POST /statements/batch** - Validate statement hashes
5. **POST /statements/cleanup-orphaned** - Validate cleanup request

#### Error Handling

**File**: `src/models/entity_api/main.py`

Added validation exception handler:

```python
@app.exception_handler(jsonschema.ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse
```

Returns HTTP 400 with detailed error messages:
```json
{
  "error": "validation_error",
  "message": "JSON schema validation failed",
  "details": [
    {
      "field": "/labels",
      "message": "Required property missing",
      "path": "#/labels"
    }
  ]
}
```

### Impact

- **API latency**: +10-50ms per request (schema validation overhead)
- **Data integrity**: 100% of stored entities valid per schema
- **Error feedback**: Immediate validation errors returned to users
- **Simplification**: Removed need for background validation service architecture
- **Testing**: Schema compliance enforced before persistence

### Backward Compatibility

- **Breaking change**: Invalid JSON that previously passed now rejected with 400 error
- **API contracts**: Aligns with existing JSON schema definitions
- **Error codes**: New validation error type added to API response format

### Future Enhancements

- Optimize schema compilation and caching to reduce validation latency
- Add detailed validation metrics for monitoring
- Consider custom validators for business logic beyond JSON schema
- Add schema versioning support for schema evolution

---

## [2026-01-05] Statement-Level Revision Tracking with Deduplication

### Summary

Implemented first-class statement-level revision tracking with automatic deduplication, enabling statements to be stable, reusable objects with their own identifiers. Statements are now stored independently of entities with hash-based deduplication across all entities, reducing storage costs and enabling advanced features like most-used statement tracking and property-based loading.

### Motivation

Wikibase requires statement-level tracking for:

- **Storage efficiency**: 20% deduplication rate expected at scale (1T statements → 800B unique)
- **Cross-entity reuse**: Same statement content shared across Q42, Q999, Q5000 without duplication
- **Property-based loading**: Frontend can load only properties needed (e.g., P31,P569 instead of all statements)
- **Most-used statements**: Scientific analysis of most referenced statements across all entities
- **Hard delete lifecycle**: Statements live forever accessible via entity revision history
- **Cost reduction**: 67 GB S3 storage vs 400 GB raw (6:1 compression + deduplication)

### Changes

#### Updated Vitess Schema

**File**: `src/models/infrastructure/vitess_client.py`

**Modified table: entity_revisions**

```sql
ALTER TABLE entity_revisions ADD COLUMN statements JSON NOT NULL;
ALTER TABLE entity_revisions ADD COLUMN properties JSON NOT NULL;
ALTER TABLE entity_revisions ADD COLUMN property_counts JSON NOT NULL;
```

**New columns**:
- `statements`: Array of statement hashes (64-bit integers), not full statement content
- `properties`: Flat array of property IDs used in this revision (e.g., ["P31", "P569", "P19"])
- `property_counts`: Map of property_id → statement count (e.g., {"P31": 2, "P569": 1})

**Modified table: statement_content**

**Fix**: Removed duplicate table definition (lines 92-99), kept single definition (lines 81-87)

**Schema**:
```python
statement_content (
    content_hash BIGINT PRIMARY KEY,  -- rapidhash of full statement JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ref_count INT DEFAULT 1,  -- Track how many entities reference this statement
    INDEX idx_ref_count (ref_count DESC)  -- Enable most-used queries
)
```

**New VitessClient methods**:

```python
# Statement lifecycle
def insert_statement_content(self, content_hash: int) -> bool
def increment_ref_count(self, content_hash: int) -> int
def decrement_ref_count(self, content_hash: int) -> int
def get_orphaned_statements(self, older_than_days: int, limit: int) -> list[int]
def get_most_used_statements(self, limit: int, min_ref_count: int = 1) -> list[int]

# Revision queries
def get_entity_properties(self, entity_id: str, revision_id: int) -> list[str]
def get_entity_property_counts(self, entity_id: str, revision_id: int) -> dict[str, int]
def get_entity_statements_by_property(
    self, entity_id: str, revision_id: int, property_id: str
) -> list[int]
```

**Rationale**:
- Hash arrays in revisions: Revisions reference statements via 64-bit hashes instead of full JSON
- Property tracking: Enables intelligent frontend loading (load only needed properties)
- Ref_count: Tracks statement usage for orphaned cleanup and most-used statistics
- Descending index: Fast queries for most-used statements (O(log n))

#### Updated S3 Storage

**File**: `src/models/infrastructure/s3_client.py`

**New S3 client methods**:

```python
def write_statement(self, content_hash: int, statement_data: dict) -> None:
    """Write statement to S3 (idempotent, deduplicated storage)"""
    key = f"statements/{content_hash}.json"

def read_statement(self, content_hash: int) -> dict:
    """Read statement from S3"""
    key = f"statements/{content_hash}.json"

def statement_exists(self, content_hash: int) -> bool:
    """Check if statement exists in S3"""
    key = f"statements/{content_hash}.json"

def batch_read_statements(self, content_hashes: list[int]) -> dict[int, dict]:
    """Batch fetch multiple statements from S3"""
```

**Updated S3 revision schema**: v1.1.0

**New fields**:
```json
{
  "statements": [987654321012345678, 123456789012345678, ...],
  "properties": ["P31", "P569", "P19", ...],
  "property_counts": {"P31": 2, "P569": 1, "P19": 1}
}
```

**New S3 statement schema**: v1.0.0

**File**: `src/schemas/s3-statement/1.0.0/schema.json`

```json
{
  "content_hash": 987654321012345678,
  "statement": {
    "mainsnak": {...},
    "type": "statement",
    "rank": "normal",
    "qualifiers": {...},
    "references": [...]
  },
  "created_at": "2026-01-05T09:00:00Z"
}
```

**Storage layout**:
- Entity revisions: `s3://wikibase-revisions/{entity_id}/rev{revision_id}.json`
- Statements: `s3://wikibase-statements/{content_hash}.json`

**Rationale**:
- Statement granularity: Complete statement block (mainsnak + qualifiers + references) hashed together
- Deduplication: Same content = one S3 object, shared across entities
- Hash-only in revisions: Revisions reference hashes instead of full JSON, minimal storage
- Property metadata: Enables intelligent frontend loading

#### New Models

**File**: `src/models/statements/statement_hasher.py`

```python
class StatementHasher:
    @staticmethod
    def compute_hash(statement: Statement) -> int:
        """Compute rapidhash of full statement JSON"""
        # Serialize to canonical JSON (sorted keys, deterministic order)
        # Return 64-bit rapidhash integer
```

**File**: `src/models/statements/extractor.py`

```python
class StatementExtractor:
    @staticmethod
    def extract_properties(entity: Entity) -> list[str]:
        """Extract unique property IDs from entity statements"""
        
    @staticmethod
    def compute_property_counts(entity: Entity) -> dict[str, int]:
        """Count statements per property"""
```

**Rationale**:
- StatementHasher: Canonical JSON serialization ensures consistent hashes for identical content
- StatementExtractor: Extract property metadata for intelligent loading

#### New API Endpoints

**File**: `src/models/entity_api/main.py`

**Statement endpoints**:

```python
GET /statement/{hash}
  → Returns: Full statement JSON from S3
  
POST /statements/batch
  → Request: {hashes: [hash1, hash2, ...]}
  → Returns: {results: {hash1: {...}, hash2: {...}, ...}}

GET /statement/most_used
  → Query params: limit=1000&min_ref_count=10&property_range=P0-P999&sort_by=ref_count_desc
  → Returns: [hash1, hash2, ...]
```

**Property endpoints**:

```python
GET /entity/{id}/properties
  → Returns: ["P31", "P569", "P19", ...]

GET /entity/{id}/properties/counts
  → Returns: {"P31": 2, "P569": 1, "P19": 1}

GET /entity/{id}/properties/P31,P569
  → Returns: [hash1, hash2, hash3, ...]
```

**Modified entity endpoints**:

```python
GET /entity/{id}?resolve_statements=false
  → Returns: Metadata + statement hashes (no full statements)

GET /entity/{id}?resolve_statements=true&properties=P31,P569
  → Returns: Metadata + full statements for specific properties only
```

**Rationale**:
- Statement endpoints: First-class citizen access to statements
- Property endpoints: Enable intelligent frontend loading
- Optional resolution: Frontend controls when to fetch full statements

#### Entity Creation Flow Updates

**File**: `src/models/entity_api/main.py`

**New workflow**:

```python
# 1. Extract statements from entity
statements = entity.statements

# 2. Hash each statement
statement_hashes = [StatementHasher.compute_hash(s) for s in statements]

# 3. Deduplicate and store statements
for stmt, hash_val in zip(statements, statement_hashes):
    s3_client.write_statement(hash_val, stmt.to_dict())
    vitess.insert_statement_content(hash_val)
    vitess.increment_ref_count(hash_val)

# 4. Extract property metadata
properties = StatementExtractor.extract_properties(entity)
property_counts = StatementExtractor.compute_property_counts(entity)

# 5. Build revision with hash array + metadata
revision = {
    "statements": statement_hashes,
    "properties": properties,
    "property_counts": property_counts,
    ...
}

# 6. Write revision to S3
s3_client.write_entity_revision(entity_id, revision_id, revision)

# 7. Insert revision metadata to Vitess
vitess.insert_revision(entity_id, revision_id, statements=statement_hashes, ...)

# 8. Update entity head
vitess.update_head(entity_id, revision_id)
```

**Rationale**:
- Deduplication: Same statement content writes to same S3 object and Vitess row
- Ref_count tracking: Incremented for each entity using the statement
- Property extraction: Computed once during entity creation

#### Entity Read Flow Updates

**File**: `src/models/entity_api/main.py`

**New workflow**:

```python
# 1. Get revision from S3 (contains hashes, not full statements)
revision = s3_client.read_entity_revision(entity_id, revision_id)

# 2. If frontend requests full statements
if resolve_statements:
    statements = s3_client.batch_read_statements(revision["statements"])
else:
    statements = []  # Return hashes only

# 3. If frontend requests specific properties
if properties_filter:
    # Filter hashes by property
    filtered_hashes = filter_hashes_by_property(revision, properties_filter)
    statements = s3_client.batch_read_statements(filtered_hashes)

# 4. Return response
return {
    "metadata": revision["metadata"],
    "statements": statements,  # or hashes if not resolved
    "properties": revision["properties"],
    "property_counts": revision["property_counts"]
}
```

**Rationale**:
- Hash-only by default: Minimal response size, frontend controls loading
- Property-based filtering: Load only statements for specific properties
- Batch fetching: Efficiently fetch multiple statements in parallel

#### Hard Delete Flow Updates

**File**: `src/models/entity_api/main.py`

**New workflow**:

```python
# 1. Get all statement hashes from entity revisions
revisions = vitess.get_history(entity_id)
all_hashes = []
for rev in revisions:
    all_hashes.extend(rev["statements"])

# 2. Decrement ref_count for each statement
for hash_val in all_hashes:
    vitess.decrement_ref_count(hash_val)

# 3. Mark entity as deleted
vitess.mark_entity_deleted(entity_id)

# 4. Schedule orphaned cleanup (background job)
# Scheduled job runs daily:
orphaned = vitess.get_orphaned_statements(older_than_days=180, limit=10000)
for hash_val in orphaned:
    s3_client.delete_statement(hash_val)
    vitess.delete_statement_content(hash_val)
```

**Rationale**:
- 180-day grace period: Orphaned statements kept for history recovery
- Ref_count tracking: Decrement when entity deleted, increment when restored
- Background cleanup: Efficiently batch-delete orphaned statements

### Impact

- **Storage efficiency**: 20% deduplication rate at scale (1T statements → 800B unique)
- **Cost reduction**: 67 GB S3 storage vs 400 GB raw (6:1 compression + deduplication)
- **Query performance**: Property-based loading reduces response size by 80-90% for typical entity queries
- **Advanced analytics**: Most-used statements endpoint enables scientific analysis
- **Storage cost**: ~$23,000/month at year 10 scale (S3 + Vitess) vs ~$92,000/month without deduplication
- **Write latency**: 500ms batch writes (statement hashing + deduplication)
- **Read latency**: 100ms reads with hash-only, 150-250ms with statement resolution

### Backward Compatibility

- Schema v1.1.0 backward compatible (new fields optional)
- Old revisions without statement hashes remain readable (migrated during next edit)
- Entity API endpoints maintain compatibility (optional resolve_statements parameter)
- S3 client methods additive (no breaking changes)

---

## [2025-01-05] Statement deduplication and statistics (archived - see above) 

## [2025-01-02] Internal ID Encapsulation

### Summary
Encapsulated internal ID resolution within VitessClient, removing exposure of internal IDs to all external code. All VitessClient methods now accept `entity_id: str` instead of `internal_id: int`, handling ID resolution internally. This aligns with the goal of keeping internal implementation details private and maintaining clean API boundaries.

### Motivation
- **Encapsulation**: Internal IDs are implementation details that shouldn't leak outside VitessClient
- **API cleanliness**: External code should work with entity IDs only (Q42, not internal ID 42)
- **Maintainability**: Changes to internal ID handling only affect VitessClient, not all calling code
- **Testing**: Simpler tests - no need to manage internal ID mappings

### Changes
#### VitessClient API Updates
**File**: `src/models/infrastructure/vitess_client.py`

**Private method**:
- `resolve_id(entity_id: str) -> int`: Made private to prevent external access
- Internal implementation: Queries entity_id_mapping table directly

**Method signature changes** (all now accept `entity_id: str`):
- `is_entity_deleted(entity_id: str) -> bool`: Check if entity is hard-deleted
- `is_entity_locked(entity_id: str) -> bool`: Check if entity is locked
- `is_entity_archived(entity_id: str) -> bool`: Check if entity is archived
- `get_head(entity_id: str) -> int`: Get current head revision
- `write_entity_revision(entity_id, revision_id, data, is_mass_edit, edit_type) -> None`: Write revision data
- `read_full_revision(entity_id: str, revision_id) -> dict`: Read full revision data
- `insert_revision(entity_id, revision_id, is_mass_edit, edit_type) -> None`: Insert revision metadata

**Internal behavior**:
- All methods now call `_resolve_id(entity_id)` internally to convert to internal IDs
- Methods that require valid entities raise `ValueError` with descriptive message
- Methods return sensible defaults (False, [], 0) if entity not found

#### RedirectService Updates
**File**: `src/services/entity_api/redirects.py`

**Removed calls**:
- No longer calls `vitess.resolve_id()` directly
- No longer manages `from_internal_id` and `to_internal_id` variables
- Simplified validation logic

**Updated flow**:
- All VitessClient calls use `entity_id: str` parameters
- VitessClient handles all internal ID resolution
- Removed manual internal ID resolution logic

#### Entity API Updates
**File**: `src/models/entity_api/main.py`

**Removed calls**:
- No longer calls `clients.vitess.resolve_id()` directly
- No longer manages `from_internal_id` and `to_internal_id` variables

**Updated methods**:
- All VitessClient calls now pass entity IDs directly
- Removed manual internal ID resolution logic
- Removed imports of `_resolve_id` (no longer needed)

#### Test Mocks Updates
**Files**: 
- `tests/test_entity_redirects.py`
- `tests/debug_Q17948861.py`

**Updated MockVitessClient**:
- `_resolve_id()` made private (mocks match real API)
- All methods updated to accept `entity_id: str` and resolve internally
- Mocked `from_internal_id` and `to_internal_id` variables removed

### Rationale
- **Encapsulation**: Internal IDs are Vitess implementation detail, not API surface
- **API cleanliness**: External code should work with entity IDs only (Q42, not internal ID 42)
- **Maintainability**: Changes to internal ID handling only affect VitessClient, not all calling code
- **Testing**: Simpler tests - no need to manage internal ID mappings

### Summary

Encapsulated internal ID resolution within VitessClient, removing exposure of internal IDs to all external code. All VitessClient methods now accept `entity_id: str` instead of `internal_id: int`, handling ID resolution internally. This aligns with the goal of keeping internal implementation details private and maintaining clean API boundaries.

### Motivation

- **Encapsulation**: Internal IDs are implementation details that shouldn't leak outside VitessClient
- **API cleanliness**: External code should work with entity IDs only (Q42, not internal ID 42)
- **Maintainability**: Changes to internal ID handling only affect VitessClient, not all calling code
- **Testing**: Simpler tests - no need to manage internal ID mappings

### Changes

#### VitessClient API Updates

**File**: `src/models/infrastructure/vitess_client.py`

**Private method**:
- `resolve_id()` → `_resolve_id()`: Made private to prevent external access

**Method signature changes** (all now accept `entity_id: str` instead of `internal_id: int`):
- `is_entity_deleted(entity_id: str)`: Check if entity is hard-deleted
- `is_entity_locked(entity_id: str)`: Check if entity is locked
- `is_entity_archived(entity_id: str)`: Check if entity is archived
- `get_head(entity_id: str)`: Get current head revision
- `write_entity_revision(entity_id: str, ...)`: Write revision data
- `read_full_revision(entity_id: str, revision_id: int)`: Read revision data
- `insert_revision(entity_id: str, ...)`: Insert revision metadata
- `get_redirect_target(entity_id: str)`: Get redirect target
- `set_redirect_target(entity_id: str, redirects_to_entity_id: str | None)`: Set redirect target
- `get_history(entity_id: str)`: Get revision history
- `hard_delete_entity(entity_id: str, head_revision_id: int)`: Permanently delete entity

**Internal behavior**:
- All methods now call `_resolve_id(entity_id)` internally to convert to internal IDs
- Methods validate entity exists and return sensible defaults (False, [], 0) if not found
- Methods that require valid entities raise `ValueError` with descriptive message

#### RedirectService Updates

**File**: `src/services/entity_api/redirects.py`

**Removed calls**:
- No longer calls `vitess.resolve_id()` directly
- No longer manages `from_internal_id` and `to_internal_id` variables

**Updated flow**:
- All VitessClient calls use `entity_id: str` parameters
- VitessClient handles all internal ID resolution
- Simplified validation logic - no need to check for `None` internal IDs

#### Entity API Updates

**File**: `src/models/entity_api/main.py`

**Removed calls**:
- No longer calls `clients.vitess.resolve_id()` directly
- `internal_id` variables replaced with direct entity_id usage

**Updated methods**:
- All VitessClient calls now pass entity IDs directly
- Removed manual internal ID resolution logic

#### Test Mocks Updates

**File**: `tests/test_entity_redirects.py`

**Updated MockVitessClient**:
- `_resolve_id()` made private (mocks match real API)
- Methods updated to accept `entity_id: str` parameters
- Internal ID resolution happens within mock methods

**Updated Mock RedirectService**:
- Removed `from_internal_id` and `to_internal_id` tracking
- All operations use entity IDs only

### Rationale

- **Encapsulation**: Internal IDs are Vitess implementation detail, not API surface
- **Type safety**: Strings (entity IDs) are less error-prone than mixing int/str IDs
- **Simplification**: External code doesn't need to understand internal ID mapping
- **Testability**: Tests focus on entity IDs, not implementation details
- **Future-proof**: If internal ID scheme changes, only VitessClient needs updates

## [2025-01-15] Entity Redirect Support

### Summary

Added redirect entity support allowing creation of redirect relationships between entities. Redirects are minimal tombstones pointing to target entities, following the immutable revision pattern. Support includes S3 schema for redirect metadata, Vitess tables for tracking relationships, Entity API for creating redirects, special revert endpoint for undoing redirects, and RDF builder integration for efficient querying.

### Motivation

Wikibase requires redirect functionality for:
- **Entity merges**: When two items are merged, source becomes a redirect to target
- **Stable identifiers**: Preserve old entity IDs that may be referenced externally
- **RDF compliance**: Generate `owl:sameAs` statements matching Wikidata format
- **Revertibility**: Redirects can be reverted back to normal entities using revision-based restore
- **Vitess efficiency**: RDF builder queries Vitess for redirect counts instead of MediaWiki API
- **Community needs**: Easy reversion to earlier entity states before redirect was created

### Changes

#### Updated S3 Revision Schema

**File**: `src/schemas/s3-revision/1.1.0/schema.json`

Added redirect metadata field:

```json
{
  "redirects_to": "Q42"  // or null for normal entities
}
```

Redirect entities have minimal structure:

```json
{
  "redirects_to": "Q42",
  "entity": {
    "id": "Q59431323",
    "labels": {},
    "descriptions": {},
    "aliases": {},
    "claims": {},
    "sitelinks": {}
  }
}
```

**Schema version bump**: 1.0.0 → 1.1.0 (MINOR - backward-compatible addition)

**Rationale**:
- `redirects_to`: Single entity ID or null, marking redirect target (or null)
- Redirect entities have empty labels, claims, sitelinks (minimal tombstone)
- Can be reverted by writing new revision with `redirects_to: null` and full entity data
- Backward compatible (null for normal entities in 1.0.0)

#### Updated Vitess Schema

**File**: `src/models/infrastructure/vitess_client.py`

**Add to entity_head table**:

```sql
ALTER TABLE entity_head ADD COLUMN redirects_to BIGINT NULL;
```

**New table: entity_redirects**

```sql
CREATE TABLE IF NOT EXISTS entity_redirects (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    redirect_from_id BIGINT NOT NULL,
    redirect_to_id BIGINT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) DEFAULT NULL,
    INDEX idx_redirect_from (redirect_from_id),
    INDEX idx_redirect_to (redirect_to_id),
    UNIQUE KEY unique_redirect (redirect_from_id, redirect_to_id)
)
```

**Updated VitessClient methods**:
- `resolve_id()` → `_resolve_id()`: Made private (internal ID resolution no longer exposed)
- `set_redirect_target()`: Mark entity as redirect in entity_head (now accepts `entity_id: str`)
- `create_redirect()`: Create redirect relationship in entity_redirects table (now accepts `entity_id: str`)
- `get_incoming_redirects()`: Query entities redirecting to target (for RDF builder) (now accepts `entity_id: str`)
- `get_redirect_target()`: Query where entity redirects to (for validation) (now accepts `entity_id: str`)
- `is_entity_deleted()`: Check if entity is hard-deleted (now accepts `entity_id: str`)
- `is_entity_locked()`: Check if entity is locked (now accepts `entity_id: str`)
- `is_entity_archived()`: Check if entity is archived (now accepts `entity_id: str`)
- `get_head()`: Get current head revision (now accepts `entity_id: str`)
- `write_entity_revision()`: Write revision data (now accepts `entity_id: str`)
- `read_full_revision()`: Read revision data (now accepts `entity_id: str`)
- `insert_revision()`: Insert revision metadata (now accepts `entity_id: str`)
- `get_history()`: Get revision history (now accepts `entity_id: str`)
- `hard_delete_entity()`: Permanently delete entity (removed `internal_id` parameter)

**Rationale**:
- `redirects_to` in entity_head: Fast check if entity is a redirect
- Separate `entity_redirects` table: Track all redirect relationships without bloating entity_head
- Bidirectional indexes: Support both incoming (RDF builder) and target (validation) queries
- Audit trail: `created_at` and `created_by` track redirect creation
- Unique constraint: Prevent duplicate redirects

#### Entity Model Updates

**File**: `src/models/entity.py`

**New models**:
```python
class EntityRedirectRequest(BaseModel):
    redirect_from_id: str  # Entity to mark as redirect (e.g., Q59431323)
    redirect_to_id: str    # Target entity (e.g., Q42)
    created_by: str = "entity-api"

class EntityRedirectResponse(BaseModel):
    redirect_from_id: str
    redirect_to_id: str
    created_at: str
    revision_id: int
```

**New EditType values**:
- `REDIRECT_CREATE = "redirect-create"`: Creating a redirect
- `REDIRECT_REVERT = "redirect-revert"`: Converting redirect back to normal entity

**Revert support models**:
```python
class RedirectRevertRequest(BaseModel):
    revert_to_revision_id: int = Field(
        ..., description="Revision ID to revert to (e.g., 12340)"
    )
    revert_reason: str = Field(
        ..., description="Reason for reverting redirect"
    )
    created_by: str = Field(default="entity-api")
```

#### Entity API Integration

**New File**: `src/services/entity_api/redirects.py`

**New RedirectService**:
- `create_redirect()`: Mark entity as redirect
  - Validates both entities exist (using Vitess, no internal ID exposure)
  - Prevents circular redirects
  - Checks for duplicate redirects (using Vitess)
  - Validates target not already a redirect
  - Validates source and target not deleted/locked/archived
  - Creates minimal S3 revision (tombstone) for redirect entity
  - Records redirect in Vitess (Vitess handles internal ID resolution internally)
  - Updates entity_head.redirects_to for source entity
  - Returns revision ID of redirect entity

- `revert_redirect()`: Revert redirect entity back to normal
  - Reads current redirect revision (tombstone)
  - Reads target entity revision to restore from
  - Writes new revision with full entity data
  - Updates entity_head.redirects_to to null (Vitess handles internal ID resolution)
  - Returns new revision ID

**New FastAPI endpoints**: 
- `POST /entities/redirects`: Create redirect
- `POST /entities/{id}/revert-redirect`: Revert redirect back to normal

**Request/Response**: 
- `EntityRedirectRequest` → `EntityRedirectResponse`
- `RedirectRevertRequest` → `EntityResponse`

#### RDF Builder Enhancements

**File**: `src/models/rdf_builder/converter.py`

**Changes**:
- Added `vitess_client` parameter to `EntityConverter.__init__()`
- Updated `_fetch_redirects()` to query Vitess for redirects
- Maintains fallback to file-based cache for test scenarios
- Priority: Vitess → File cache → Empty list

**File**: `src/models/rdf_builder/redirect_cache.py`

**New method**:
```python
def load_entity_redirects_from_vitess(
    entity_id: str, vitess_client: VitessClient
) -> list[str]:
    """Load redirects from Vitess authoritative data source"""
```

**Rationale**:
- RDF builder queries Vitess for redirects (authoritative source)
- Eliminates MediaWiki API dependency in production
- File-based cache still works for test scenarios
- Support efficient redirect count queries for UI

### Impact

- **RDF Builder**: Queries Vitess for redirects (authoritative source), no MediaWiki dependency
- **Entity API**: Can create/revert redirects via S3 + Vitess (immutable snapshots)
- **Readers**: Redirects visible in S3 revision history, queryable via Vitess
- **Revertibility**: Redirects can be undone by writing new revision with normal entity data using revision-based restore
- **Query Performance**: Indexed Vitess lookups (O(log n) for large entity sets)
- **Vitess Awareness**: Vitess knows redirect counts (e.g., Q42 has 4 incoming redirects)

### Backward Compatibility

- Schema 1.1.0 is backward compatible with 1.0.0 (redirects_to field optional)
- Normal entities have `redirects_to: null` (or omitted)
- Redirect entities have minimal entity structure + `redirects_to` field
- Existing readers ignore unknown fields
- RDF builder falls back to file cache if Vitess unavailable

### Future Enhancements

- Update target entity S3 revision to include new redirect in `redirects` array (currently no-op)
- Batch redirect creation for mass merges
- Redirect chain validation (detect circular multi-hop)
- Redirect deletion/undo operations
- Redirect statistics and metrics API
- Redirect import/export operations for bulk data migration

---

## [2025-12-28] Entity Deletion (Soft and Hard Delete)

### Summary

Added entity deletion functionality supporting both soft deletes (default) and hard deletes (exceptional). Soft deletes create tombstone revisions preserving entity history, while hard deletes mark entities as hidden with full audit trail.

### Motivation

Wikibase requires deletion capabilities for:
- Removing inappropriate content
- Privacy/GDPR compliance
- Data cleanup operations
- Removing test/duplicate entities
- Handling user deletion requests

### Changes

#### Updated S3 Revision Schema

**File**: `src/schemas/s3-revision/1.0.0/schema.json`

Added deletion-related fields to revision schema:

```json
{
  "is_deleted": true,
  "is_redirect": false,
  "deletion_reason": "Privacy request",
  "deleted_at": "2025-12-28T10:30:00Z",
  "deleted_by": "admin-user",
  "entity": {...}
}
```

**Fields**:
- `is_deleted`: Boolean flag indicating if revision is a deletion tombstone
- `is_redirect`: Boolean flag indicating if entity is a redirect
- `deletion_reason`: Human-readable reason for deletion (required if is_deleted=true)
- `deleted_at`: ISO-8601 timestamp of deletion action
- `deleted_by`: User or system that requested deletion

**Rationale**:
- Soft delete preserves entity data in `entity` field for audit/history
- Deletion metadata stored in revision snapshot for complete trail
- `deleted_at` separate from `created_at` for clarity

#### Updated Vitess Schema

**File**: `src/infrastructure/vitess_client.py` - `_create_tables()` method

**Changes to entity_head table**:
```sql
ALTER TABLE entity_head ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE;
ALTER TABLE entity_head ADD COLUMN is_redirect BOOLEAN DEFAULT FALSE;
```

**Rationale**:
- `is_deleted` flag in entity_head enables fast filtering of hard-deleted entities
- `is_redirect` flag in entity_head enables fast checking of redirect status
- Deletion metadata stored in revision snapshots for complete audit trail

#### New Pydantic Models

**File**: `src/services/shared/models/entity.py`

Added new models and enums:

```python
class DeleteType(str, Enum):
    SOFT = "soft"
    HARD = "hard"

class EntityDeleteRequest(BaseModel):
    delete_type: DeleteType = Field(default=DeleteType.SOFT)
    deletion_reason: str = Field(..., description="Reason for deletion")
    deleted_by: str = Field(..., description="User requesting deletion")

class EntityDeleteResponse(BaseModel):
    id: str
    revision_id: int
    delete_type: DeleteType
    deleted: bool
    deleted_at: str
    deletion_reason: str
    deleted_by: str
```

### Impact

- Readers: Initial implementation
- Writers: Initial implementation
- Migration: N/A (baseline schema)

### Notes

- Establishes canonical JSON format for immutable S3 snapshots
- Entity ID stored in S3 path and entity.id, not metadata
- `revision_id` must be monotonic per entity
- `content_hash` provides integrity verification and idempotency
