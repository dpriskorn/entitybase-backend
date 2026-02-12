# Entity Model

## Entity

An entity is a logical identifier representing a Wikibase item, property, lexeme, or entity schema.

- `entity_id` (e.g. Q123, P42, L999, E100)
- `entity_type` (item, property, lexeme, entityschema)

Entities have no intrinsic state outside of revisions.

## External Entity Identifier

The **external entity ID** (e.g., `Q123`, `P42`, `L999`, `E100`) is the permanent public-facing identifier used throughout the ecosystem:

- **API endpoints**: `/entities/Q123`, `/entities/items`, `/entities/properties`
- **SPARQL queries**: `SELECT ?item WHERE { ?item wdt:P31 wd:Q123 }`
- **RDF/JSON data**: Cross-entity references in claims use Q123
- **RDF triples**: `<http://www.wikidata.org/entity/Q42> a wikibase:Item`
- **RDF change events**: `entity_id: "Q42"` in event schemas
- **S3 paths**: Human-readable inspection (e.g., `s3://wikibase-revisions/Q123/42.json`)

**Characteristics:**

- **Human-readable**: Easy to communicate and debug
- **Stable**: Never changes, permanent contract with external ecosystem
- **Compatible**: Works with all Wikidata tools, SPARQL queries, existing datasets
- **Semantic**: Prefix indicates entity type (Q=item, P=property, L=lexeme, E=entityschema)

## Range-Based ID Generation

Entity IDs are generated using a **range-based allocation system** for efficient, high-throughput ID generation.

### ID Ranges Table

The `id_ranges` table manages ID allocation:

```sql
CREATE TABLE id_ranges (
    entity_type VARCHAR(50) PRIMARY KEY,
    current_range_start BIGINT UNSIGNED NOT NULL,
    current_range_end BIGINT UNSIGNED NOT NULL,
    next_id BIGINT UNSIGNED NOT NULL,
    range_size BIGINT UNSIGNED NOT NULL DEFAULT 1000,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

- `entity_type`: Entity type (item, property, lexeme, entityschema)
- `current_range_start`: Start of the current reserved range
- `current_range_end`: End of the current reserved range
- `next_id`: Next ID to allocate
- `range_size`: Number of IDs in each reserved range

### ID Generation Process

**Initialization (via Dev Worker):**
```sql
INSERT INTO id_ranges (entity_type, current_range_start, current_range_end, next_id, range_size)
VALUES
    ('item', 1, 1000, 1, 1000),
    ('property', 1, 1000, 1, 1000),
    ('lexeme', 1, 1000, 1, 1000),
    ('entityschema', 1, 1000, 1, 1000);
```

**ID Allocation (via IdGenerationWorker):**
1. Worker polls `id_ranges` table
2. If `next_id >= current_range_end`, reserve new range: `UPDATE id_ranges SET current_range_start = current_range_end + 1, current_range_end = current_range_end + range_size, next_id = current_range_start WHERE entity_type = ?`
3. Atomically increment and claim ID: `UPDATE id_ranges SET next_id = next_id + 1 WHERE entity_type = ? AND next_id = ?`
4. Format ID with prefix (Q/P/L/E)
5. Cache in memory for fast allocation

**Atomic ID Claim (during entity creation):**
1. Check cached ID availability
2. If available, claim and use
3. If exhausted, request new range from worker
4. Confirm ID usage after successful entity creation

### EnumerationService

The `EnumerationService` provides thread-safe ID allocation:

```python
class EnumerationService:
    def allocate_id(self, entity_type: EntityType) -> str:
        """Allocate the next available ID for an entity type."""
        # Returns formatted ID (e.g., "Q123")
```

**Features:**
- Thread-safe ID allocation
- In-memory caching for low-latency allocation
- Automatic range reservation when cache exhausted
- Confirmation mechanism to reclaim unused IDs on failure

## Entity ID vs Internal ID

The current architecture uses **entity_id strings** throughout the system:

### Vitess Tables

All tables use `entity_id` as the primary key or foreign key:

```sql
entity_head
- entity_id VARCHAR(50) PRIMARY KEY
- head_revision_id BIGINT UNSIGNED NOT NULL
- updated_at TIMESTAMP NOT NULL

entity_revisions
- entity_id VARCHAR(50) NOT NULL
- revision_id BIGINT UNSIGNED NOT NULL
- content_hash BIGINT UNSIGNED NOT NULL
- PRIMARY KEY (entity_id, revision_id)

entity_redirects
- entity_id VARCHAR(50) PRIMARY KEY
- redirects_to VARCHAR(50) NOT NULL

statement_content
- content_hash BIGINT UNSIGNED PRIMARY KEY
- ref_count BIGINT UNSIGNED NOT NULL DEFAULT 1
```

**No `entity_id_mapping` table exists.** Entity IDs are used directly.

### Advantages of Current Design

- **Simplicity**: No translation layer needed
- **Human-readable**: All database queries use familiar Q123/P42 IDs
- **Debugging**: Easier to inspect database state
- **Compatibility**: Direct mapping to Wikidata IDs

## Usage Examples

### Entity Creation

```
Client Request
POST /entities/items
{
  "type": "item",
  "labels": {"en": {"language": "en", "value": "Douglas Adams"}},
  "claims": {...}
}
↓
API Layer (EntityCreateHandler)
1. Validate JSON schema (Pydantic)
2. Create CreationTransaction
3. Allocate next ID via EnumerationService (returns "Q123")
4. Register entity in Vitess (entity_head)
5. Process statements: hash, deduplicate, store in S3/Vitess (increment ref_counts)
6. Create revision: store in S3/Vitess (entity_revisions)
7. Publish change event (optional)
8. Commit transaction (confirm ID usage to worker)
9. On failure: Rollback all operations (delete from Vitess/S3, decrement ref_counts)
↓
Client Response
{
  "id": "Q123",
  "revision_id": 1,
  "created_at": "2025-01-15T10:30:00Z"
}
```

### Entity Read

```
Client Request
GET /entities/Q123
↓
API Layer
1. Query entity_head:
   SELECT head_revision_id, updated_at FROM entity_head WHERE entity_id = "Q123"
2. Query entity_revisions for content_hash:
   SELECT content_hash FROM entity_revisions WHERE entity_id = "Q123" AND revision_id = ?
3. Fetch S3 snapshot:
   GET s3://wikibase-revisions/123456789
4. Reconstruct entity from S3 data + hash references
↓
Client Response
{
  "id": "Q123",
  "revision_id": 42,
  "entity": {...entity content...}
}
```

### Property Creation

```
Client Request
POST /entities/properties
{
  "type": "property",
  "datatype": "string",
  "labels": {"en": {"language": "en", "value": "name"}}
}
↓
API Layer (PropertyCreateHandler)
1. Validate request
2. Allocate property ID via EnumerationService (returns "P42")
3. Register property in Vitess
4. Process statements (no claims for properties)
5. Create revision
6. Commit transaction
↓
Client Response
{
  "id": "P42",
  "revision_id": 1,
  "created_at": "2025-01-15T11:00:00Z"
}
```

## Storage Example

```text
S3 Object Path (content_hash-based):
  s3://wikibase-revisions/123456789

Vitess Tables:
  entity_head:
    entity_id: "Q123" (PRIMARY KEY)
    head_revision_id: 42
    updated_at: "2025-01-15T10:30:00Z"

  entity_revisions:
    entity_id: "Q123"
    revision_id: 42
    content_hash: 123456789
    created_at: "2025-01-15T10:30:00Z"

  id_ranges:
    entity_type: "item"
    current_range_start: 1
    current_range_end: 1000
    next_id: 124
```

## Key Principles

1. **ID Stability**: Q123 never changes, maintains 100% ecosystem compatibility
2. **Range-Based Allocation**: Efficient ID generation with minimal database contention
3. **Worker-Assisted**: IdGenerationWorker pre-allocates ranges for low-latency allocation
4. **Direct Usage**: Entity IDs used directly in all tables (no mapping layer)
5. **Prefix Semantics**: Q/P/L/E prefixes indicate entity type throughout system

## ID Generation Worker

**File**: `src/models/workers/id_generation/id_generation_worker.py`

**Purpose**: Background worker that reserves ID ranges to ensure high-throughput entity creation.

**Process**:
1. Monitors `id_ranges` table
2. When `next_id` approaches `current_range_end`, reserves new range
3. Continuously polls to ensure ranges are always available
4. Provides health checks for monitoring

**Configuration**:
- `WORKER_ID`: Unique worker identifier (default: auto-generated)

## Historical Note

Previous documentation described a hybrid ID strategy with `ulid-flake` internal IDs and an `entity_id_mapping` table. This was never implemented. The current architecture uses entity_id strings directly with range-based allocation, which is simpler and more maintainable.

## References

- [STORAGE-ARCHITECTURE.md](./STORAGE-ARCHITECTURE.md) - S3 and Vitess storage design
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Overall system architecture
- [WORKERS.md](./WORKERS.md) - Worker architecture including IdGenerationWorker
