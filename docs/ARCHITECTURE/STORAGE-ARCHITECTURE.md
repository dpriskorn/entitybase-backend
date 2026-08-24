# Storage Architecture

## Overview

Entitybase uses **MariaDB as the system of record** for all entity data, with S3 used exclusively for dump file uploads.

### Core Principles

- **MariaDB is the system of record**: All entity content stored as immutable snapshots in `entity_revision_data`
- **Content-hash addressing**: Revisions addressed by deterministic hashes (rapidhash)
- **Content deduplication**: Statements, references, qualifiers, snaks, terms, and sitelinks deduplicated across revisions
- **S3 for dumps only**: S3 stores RDF dump file uploads in the `wikibase-dumps` bucket

> **A revision is an immutable snapshot stored in MariaDB.**
> Once written, it never changes.

Consequences:
- No mutable revisions
- No stored diffs
- No page-based state
- Perfect audit trail
- Single database for all reads (no cross-system lookups)

---

## 3.1 MariaDB Storage - System of Record

MariaDB stores **all entity content** as immutable snapshots.

### Revision Data Storage

**entity_revision_data** - Immutable revision content
```sql
CREATE TABLE entity_revision_data (
    content_hash BIGINT UNSIGNED PRIMARY KEY,
    data JSON NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
```

**entity_revisions** - Revision metadata with content reference
```sql
CREATE TABLE entity_revisions (
    entity_id VARCHAR(50) NOT NULL,
    revision_id BIGINT UNSIGNED NOT NULL,
    content_hash BIGINT UNSIGNED NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    editor_id INT UNSIGNED NOT NULL,
    edit_summary VARCHAR(500) NOT NULL,
    is_mass_edit BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (entity_id, revision_id),
    INDEX idx_created_at (created_at),
    INDEX idx_content_hash (content_hash)
) ENGINE=InnoDB;
```

**entity_head** - Current state of each entity
```sql
CREATE TABLE entity_head (
    entity_id VARCHAR(50) PRIMARY KEY,
    head_revision_id BIGINT UNSIGNED NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;
```

### Revision Schema

Each `entity_revision_data.data` row contains a full entity snapshot:

```json
{
  "schema_version": "4.0.0",
  "entity": {
    "id": "Q123",
    "type": "item"
  },
  "labels": {"en": "Earth", "de": "Erde"},
  "descriptions": {"en": "planet in the Solar System"},
  "aliases": {"en": ["Terra"]},
  "sitelinks": {"enwiki": "Earth"},
  "statements": {
    "P31": [
      {
        "mainsnak": {"property": "P31", "datavalue": {"type": "wikibase-entityid", "value": {"id": "Q517"}}},
        "qualifiers": {},
        "references": []
      }
    ]
  },
  "redirects_to": null
}
```

**Key Features:**
- Full entity data stored inline in JSON (no hash references for content)
- Content-hash addressing preserved: hash of full entity data is the `content_hash` key
- Deterministic hashing via rapidhash ensures same content always produces same hash
- Enables efficient deduplication across revisions via `entity_revision_data` dedup
- All data in one place for fast reads

### Deduplicated Content Tables

Content is deduplicated across revisions by storing unique content once and referencing by hash.

**statement_content** - Deduplicated statements
```sql
CREATE TABLE statement_content (
    content_hash BIGINT UNSIGNED PRIMARY KEY,
    data JSON NOT NULL,
    ref_count BIGINT UNSIGNED NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_ref_count (ref_count)
) ENGINE=InnoDB;
```

**entity_redirects** - Entity redirects
```sql
CREATE TABLE entity_redirects (
    entity_id VARCHAR(50) PRIMARY KEY,
    redirects_to VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_redirects_to (redirects_to)
) ENGINE=InnoDB;
```

**entity_backlinks** - Backlink tracking
```sql
CREATE TABLE entity_backlinks (
    entity_id VARCHAR(50) NOT NULL,
    backlink_id VARCHAR(50) NOT NULL,
    property_id VARCHAR(50) NOT NULL,
    added_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (entity_id, backlink_id, property_id),
    INDEX idx_backlink (backlink_id, property_id)
) ENGINE=InnoDB;
```

### ID Generation

**id_ranges** - Range-based ID allocation
```sql
CREATE TABLE id_ranges (
    entity_type VARCHAR(50) PRIMARY KEY,
    current_range_start BIGINT UNSIGNED NOT NULL,
    current_range_end BIGINT UNSIGNED NOT NULL,
    next_id BIGINT UNSIGNED NOT NULL,
    range_size BIGINT UNSIGNED NOT NULL DEFAULT 1000,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;
```

### Lexeme Tables

**lexeme_terms** - Lexeme form representations and sense glosses
```sql
CREATE TABLE lexeme_terms (
    entity_id VARCHAR(50) NOT NULL,
    form_id VARCHAR(50) NOT NULL,
    sense_id VARCHAR(50) NOT NULL DEFAULT '',
    language_code VARCHAR(10) NOT NULL,
    content_hash BIGINT UNSIGNED NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (entity_id, form_id, sense_id, language_code),
    INDEX idx_content_hash (content_hash)
) ENGINE=InnoDB;
```

### User and Social Features

**users** - User metadata
```sql
CREATE TABLE users (
    id INT UNSIGNED PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;
```

**user_thanks** - Thanks between users
```sql
CREATE TABLE user_thanks (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    user_id INT UNSIGNED NOT NULL,
    thanked_user_id INT UNSIGNED NOT NULL,
    entity_id VARCHAR(50) NOT NULL,
    revision_id BIGINT UNSIGNED NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_thank (user_id, entity_id, revision_id),
    INDEX idx_entity_revision (entity_id, revision_id),
    INDEX idx_thanked_user (thanked_user_id, created_at)
) ENGINE=InnoDB;
```

**user_statement_endorsements** - Statement endorsements
```sql
CREATE TABLE user_statement_endorsements (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    user_id INT UNSIGNED NOT NULL,
    statement_hash BIGINT UNSIGNED NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    removed_at TIMESTAMP NULL,
    UNIQUE KEY uk_endorsement (user_id, statement_hash),
    INDEX idx_statement (statement_hash, removed_at),
    INDEX idx_user (user_id, created_at)
) ENGINE=InnoDB;
```

**user_watchlist** - User watchlist
```sql
CREATE TABLE user_watchlist (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    user_id INT UNSIGNED NOT NULL,
    entity_id VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_notification_at TIMESTAMP NULL,
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    watched_properties TEXT NOT NULL DEFAULT '',
    UNIQUE KEY uk_watch (user_id, entity_id),
    INDEX idx_user_entity (user_id, entity_id),
    INDEX idx_last_notification (last_notification_at)
) ENGINE=InnoDB;
```

**watchlist_notifications** - Watchlist notifications
```sql
CREATE TABLE watchlist_notifications (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    user_id INT UNSIGNED NOT NULL,
    entity_id VARCHAR(50) NOT NULL,
    revision_id BIGINT UNSIGNED NOT NULL,
    change_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_checked BOOLEAN NOT NULL DEFAULT FALSE,
    INDEX idx_user (user_id, created_at, is_checked),
    INDEX idx_entity (entity_id, created_at)
) ENGINE=InnoDB;
```

### Statistics Tables

**user_daily_stats** - Daily user statistics
```sql
CREATE TABLE user_daily_stats (
    stat_date DATE PRIMARY KEY,
    total_users BIGINT UNSIGNED NOT NULL,
    active_users BIGINT UNSIGNED NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
```

**general_daily_stats** - Daily general statistics
```sql
CREATE TABLE general_daily_stats (
    stat_date DATE PRIMARY KEY,
    total_statements BIGINT UNSIGNED NOT NULL,
    total_qualifiers BIGINT UNSIGNED NOT NULL,
    total_references BIGINT UNSIGNED NOT NULL,
    total_items BIGINT UNSIGNED NOT NULL,
    total_lexemes BIGINT UNSIGNED NOT NULL,
    total_properties BIGINT UNSIGNED NOT NULL,
    total_sitelinks BIGINT UNSIGNED NOT NULL,
    total_terms BIGINT UNSIGNED NOT NULL,
    terms_per_language JSON,
    terms_by_type JSON,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
```

**backlink_statistics** - Periodic backlink statistics
```sql
CREATE TABLE backlink_statistics (
    entity_id VARCHAR(50) PRIMARY KEY,
    backlink_count INT UNSIGNED NOT NULL,
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_backlink_count (backlink_count DESC)
) ENGINE=InnoDB;
```

### Metadata Tables

**metadata** - Entity metadata
```sql
CREATE TABLE metadata (
    entity_id VARCHAR(50) PRIMARY KEY,
    deleted BOOLEAN NOT NULL DEFAULT FALSE,
    semi_protected BOOLEAN NOT NULL DEFAULT FALSE,
    locked BOOLEAN NOT NULL DEFAULT FALSE,
    archived BOOLEAN NOT NULL DEFAULT FALSE,
    dangling BOOLEAN NOT NULL DEFAULT FALSE,
    mass_edit_protected BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;
```

---

## 3.2 S3 Storage - Dump File Uploads Only

S3 is used **exclusively** for storing RDF dump files. It is **not** used as a system of record for any entity data.

### Bucket

| Bucket | Purpose | Content Type |
|--------|---------|--------------|
| `wikibase-dumps` | RDF dump file uploads | Turtle (.ttl) |

### Object Paths

**Dump files**:
```
s3://wikibase-dumps/{date}/{entity_id}.ttl
Example: s3://wikibase-dumps/2026-04-10/Q123.ttl
```

### MyS3Client

The `MyS3Client` class is simplified to handle only:
- Uploading RDF dump files to the `wikibase-dumps` bucket
- Coordinating statement/metadata storage via MariaDB (not S3)

---

## 4. Read/Write Flow

### 4.1 Write Flow

**Sequence (strict order):**

```
Client Request
  ↓
API Handler (Create/Update)
  ↓
1. Validate JSON schema (Pydantic)
  ↓
2. Create Transaction (CreationTransaction or UpdateTransaction)
  ↓
3. Process content:
   - Hash and deduplicate statements via statement_content table
   - Store statements in MariaDB (not S3)
  ↓
4. Assign next revision_id (auto-increment in entity_revisions)
  ↓
5. Compute content_hash of full entity snapshot (rapidhash)
   ↓
6. Insert revision data into entity_revision_data (content_hash → JSON)
   ↓
7. Insert revision metadata into entity_revisions
  ↓
8. CAS update entity_head (new revision becomes head)
  ↓
9. Update statement_content ref_counts
  ↓
10. Publish change event to Kafka (optional)
  ↓
11. Confirm ID usage (for entity creation)
  ↓
12. Commit transaction

On failure:
  - Rollback MariaDB changes (automatic)
  - Decrement ref_counts for orphaned content
  - Confirm ID usage failure (cancel reserved range)
```

**Transaction Safety:**
- All MariaDB operations wrapped in ACID database transaction
- No external system operations (S3) required for entity CRUD
- Ref counts ensure consistency
- ID ranges only confirmed after successful commit

### 4.2 Read Flows

**GET /entities/{entity_id}**
```
1. Query entity_head for head_revision_id
2. Query entity_revisions for content_hash
3. Query entity_revision_data for JSON data
4. Parse JSON and reconstruct full entity response
5. Return JSON
```

**GET /entities/{entity_id}/revision/{revision_id}**
```
1. Query entity_revisions for content_hash
2. Query entity_revision_data for JSON data
3. Return JSON
```

**GET /entities/{entity_id}/history**
```
1. Query entity_revisions for entity_id
2. Return list of revision metadata (no entity_revision_data load needed)
3. Response: revision_id, created_at, editor, edit_summary
```

**GET /statements/{hash}**
```
1. Check statement_content table exists and ref_count > 0
2. Return statement data from statement_content.data
```

**GET /entities/{entity_id}.ttl (RDF)**
```
1. Load entity via GET /entities/{entity_id}
2. Convert to RDF using RDFBuilder
3. Return Turtle format
```

---

## 5. Deduplication Architecture

### 5.1 Content Hashing

All content is hashed using **rapidhash** for fast computation and good distribution:

- **Revisions**: Hash of full entity JSON snapshot
- **Statements**: Hash of mainsnak + qualifiers + references
- **References**: Hash of snaks array
- **Qualifiers**: Hash of snak hash array
- **Snaks**: Hash of property_id + datavalue
- **Terms**: Hash of language_code + value
- **Sitelinks**: Hash of title

### 5.2 Reference Counting

**statement_content** table tracks how many revisions use each statement:

```
Initial store: ref_count = 1
Reuse: SELECT ref_count FROM statement_content WHERE content_hash = ?; UPDATE statement_content SET ref_count = ref_count + 1
Delete: UPDATE statement_content SET ref_count = ref_count - 1
Cleanup: DELETE FROM statement_content WHERE ref_count = 0
```

**Orphaned Content Cleanup:**

```python
def cleanup_orphaned_statements():
    # Find statements with ref_count = 0
    orphans = query("SELECT content_hash FROM statement_content WHERE ref_count = 0")
    # Delete from database
    delete("DELETE FROM statement_content WHERE ref_count = 0")
```

### 5.3 Storage Efficiency

Deduplication provides massive storage savings:

- **Statements**: Typical entity shares 30-50% of statements with other entities
- **Terms**: "United States" label appears in millions of entities (single copy)
- **References**: Common citations (e.g., Wikipedia articles) shared across thousands of statements
- **Sitelinks**: Same page titles shared across entities

**Estimated savings**: ~90% reduction in total storage compared to inline storage.

---

## 6. Schema Versioning

All revision data includes schema version for evolution:

| Schema | Version | Status | Notes |
|--------|---------|--------|-------|
| Entity (response) | 2.0.0 | Current | Full entity JSON |
| Revision (storage) | 4.0.0 | Current | Full entity snapshot in JSON |
| Statement | 1.0.0 | Current | Hash-referenced snaks |
| Reference | 1.0.0 | Current | Hash-referenced snaks |
| Qualifier | 1.0.0 | Current | Hash-referenced snaks |
| Snak | 1.0.0 | Current | Atomic datavalue |

---

## 7. Performance Characteristics

### MariaDB
- **Write latency**: ~10-50ms per transaction (all operations in single DB)
- **Read latency**: ~5-20ms per query (no cross-system lookups)
- **Sharding**: Not currently implemented (single shard)
- **Connection pooling**: Configurable pool size

### Combined Read Path
- **Total latency**: ~50-100ms per entity read (single database query chain)
- **Optimization**: Content-hash deduplication reduces storage size
- **Caching**: Entity responses cached in Redis (optional)

---

## 8. Data Integrity

### Transaction Safety
- All MariaDB writes wrapped in ACID transactions
- No external system operations required for entity CRUD
- Ref counts ensure consistency

### Hash Verification
- Content hash computed before storage
- Hash verified on retrieval (optional, for debugging)
- Rapidhash provides collision resistance

### Rollback Handling
```
On transaction failure:
1. Rollback MariaDB transaction (automatic)
2. Decrement ref_counts for orphaned content
3. Confirm ID usage failure (cancel reserved range)
```

---

## References

- [ENTITY-MODEL.md](./ENTITY-MODEL.md) - Entity ID strategy and models
- [REPOSITORIES.md](./REPOSITORIES.md) - Repository classes for data access
- [STATEMENT-DEDUPLICATION.md](./STATEMENT-DEDUPLICATION.md) - Statement deduplication details
- [S3-REVISION-ID-STRATEGY.md](./S3/S3-REVISION-ID-STRATEGY.md) - Revision ID strategy
- [S3-REVISION-SCHEMA-EVOLUTION.md](./S3/S3-REVISION-SCHEMA-EVOLUTION.md) - Schema evolution and migration
