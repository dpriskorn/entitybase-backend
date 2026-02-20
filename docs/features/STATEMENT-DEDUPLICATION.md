# Statement-Level Revision Tracking Architecture

## Executive Summary

First-class statement-level revision tracking at 1 trillion statement scale. MVP greenfield implementation with zero migration requirements.

## Key Architectural Decisions

- Statement IDs: Hash-only (no S-IDs, no mapping table)
- Statement Granularity: Full statement block (mainsnak + qualifiers + references)
- Deletion Lifecycle: Statements live forever (accessible via entity revision history)
- Deduplication: Automatic via hash PRIMARY KEY (rapidhash)
- Entity Revisions: Store hash arrays + properties + property_counts
- Property-Based Loading: Intelligent frontend loading, demand-fetch only
- Most-Used Statements: `/statement/most_used` endpoint for scientific analysis
- Hard Delete Cleanup: Ref-count tracking with 180-day grace period
- No Migration: Optimal architecture from day one (MVP greenfield)

## Conceptual Model

### Entity

Logical identifier only, no intrinsic state outside revisions.

- `entity_id` (e.g., Q123)
- `entity_type` (item, property, lexeme, …)

### Statement

First-class citizen with stable identifier (hash).

- `statement_hash` (rapidhash of statement JSON): 64-bit integer
- Immutable snapshot of claims data including:
  - mainsnak
  - type
  - rank
  - qualifiers
  - references

### Lifecycle

**Creation**

1. Hash computed: `rapidhash(statement_json)`
2. S3 object created: `statements/{hash}.json`
3. Database record: `INSERT INTO statement_content (content_hash, created_at)`

**Deduplication**

If same statement content appears:
1. Hash already exists in `statement_content` table
2. S3 object already exists
3. Only ref_count increment needed

**Usage Tracking**

When statement added to entity revision:
1. Entity revision stores hash: `statements: [hash1, hash2, ...]`
2. `ref_count` in `statement_content` incremented

**Deletion (Entity Hard-Delete)**

1. `ref_count` decremented for all statements used by entity
2. If `ref_count` reaches 0: cleanup job schedules deletion (180-day grace period)
3. Statement object deleted from S3 and database
4. Statement remains accessible via historical entity revisions

## Storage Architecture

### S3 Storage

**Entity Revisions**

```
s3://wikibase-revisions/entity/Q42/rev100.json
```

```json
{
  "schema_version": "1.0.0",
  "revision_id": 100,
  "created_at": "2026-01-05T10:00:00Z",
  "entity_id": "Q42",
  "statements": [hash1, hash2, hash3],
  "properties": ["P31", "P569", "P19"],
  "property_counts": {"P31": 2, "P569": 1, "P19": 1},
  "content_hash": 11223344556677889,
  "metadata": {
    "labels": {...},
    "descriptions": {...}
  }
}
```

**Statements**

```
s3://wikibase-statements/987654321012345678.json
```

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

**Storage Projections (1T statements)**

- Unique statements: 800B
- Raw storage: 400 GB
- Compressed (6:1 Brotli): 67 GB
- Cost (S3 Standard): $1,541/month
- Cost (Intelligent-Tiering): ~$536/month

### Vitess Schema

**Statement Content**

```sql
statement_content (
    content_hash BIGINT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ref_count INT DEFAULT 1,
    INDEX idx_ref_count (ref_count DESC)
)
```

**Entity Revisions**

```sql
entity_revisions (
    entity_id BIGINT NOT NULL,
    revision_id BIGINT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    statements JSON NOT NULL,
    is_mass_edit BOOLEAN DEFAULT FALSE,
    edit_type VARCHAR(100) DEFAULT '',
    PRIMARY KEY (entity_id, revision_id),
    INDEX idx_created (created_at)
)
```

**Entity Head**

```sql
entity_head (
    entity_id BIGINT PRIMARY KEY,
    head_revision_id BIGINT NOT NULL,
    is_semi_protected BOOLEAN DEFAULT FALSE,
    is_locked BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,
    is_dangling BOOLEAN DEFAULT FALSE,
    is_mass_edit_protected BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    is_redirect BOOLEAN DEFAULT FALSE,
    redirects_to BIGINT NULL,
    updated_at TIMESTAMP
)
```

**Storage Projections (1T statements)**

- statement_content: 80 GB
- entity_revisions: 1 TB
- entity_head: 50 GB
- Total: ~1.18 TB

## API Surface

### Entity Endpoints

- `GET /entity/{id}` → Metadata + statement hashes + properties + counts
- `GET /entity/{id}/revision/{rev_id}` → Historical entity revision
- `GET /entity/{id}/properties` → Flat property IDs array
- `GET /entity/{id}/properties/counts` → Statement counts per property
- `GET /entity/{id}/properties/{prop_id}` → Hashes for specific property

### Statement Endpoints

- `GET /statement/{hash}` → Full statement JSON from S3
- `POST /statements/batch` → Batch fetch multiple statements
- `GET /statement/most_used` → Most referenced statements

**Most-Used Query Parameters**

- `limit=1000`
- `offset=0`
- `min_ref_count=10`
- `property_range=P0-P999`
- `sort_by=ref_count_desc`

## Orphaned Statement Cleanup

**Hard Delete Flow**

```sql
-- Step 1: Decrement ref_count
UPDATE statement_content
SET ref_count = ref_count - 1
WHERE content_hash IN (
    SELECT content_hash
    FROM entity_revisions
    WHERE entity_id = Q42_internal_id
    AND revision_id = Q42_rev_100
)

-- Step 2: Mark entity as deleted
UPDATE entity_head
SET is_deleted = TRUE
WHERE entity_id = Q42_internal_id
```

## Implementation Phases

### Phase 1: Database Schema

- Create `statement_content` table
- Modify `entity_revisions` to store hash arrays
- Create S3 object models

### Phase 2: Core Logic

- Implement hash computation and deduplication
- Implement entity revision creation with properties + counts
- Implement ref_count tracking

### Phase 3: API Endpoints

- Entity endpoints with property-based filtering
- Statement endpoints with batch fetching
- Most-used statements query

### Phase 4: Integration

- Frontend integration with demand-loading
- Hard delete with orphaned cleanup
- Performance testing and optimization

## Success Criteria

- Database schema supports hash-based statements
- Entity revisions store hash arrays (not full statements)
- Statement deduplication working (same content = one S3 object)
- Property-based loading implemented
- Statement endpoints operational
- Most-used statements endpoint functional
- Hard delete with orphaned cleanup working
- Performance targets met (100ms reads, 500ms batch writes)
- Storage projections validated (1T statements achievable)

## Performance Projections

**Query Latency**

- `GET /entity/Q42`: 55-110ms
- `GET /statement/{hash}`: 50-100ms
- `GET /statement/most_used`: 110-210ms

**Cost (1T statements)**

- S3: $536-$1,541/month
- Vitess: ~$22,500/month
- Total: ~$23,000/month (Year 10)
