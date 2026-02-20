# Storage Architecture

## Overview

Entitybase uses a hybrid storage architecture combining **S3 for immutable content** and **Vitess for metadata and indexing**.

### Core Principles

- **S3 is the system of record**: All entity content stored as immutable snapshots
- **Vitess is for metadata only**: Stores pointers, indexes, and relationships
- **Content deduplication**: Statements, references, qualifiers, snaks, terms, and sitelinks deduplicated across revisions
- **Hash-based references**: Content addressed by integer hashes for efficiency

> **A revision is an immutable snapshot stored in S3.**
> It is written once and never changes.

Consequences:
- No mutable revisions
- No stored diffs
- No page-based state
- Perfect audit trail
- CDN-friendly for global distribution

---

## 3.1 S3 Storage - System of Record

S3 stores **all entity content** as immutable snapshots.

### Storage Buckets

| Bucket | Purpose | Schema Version | Content Type |
|--------|---------|----------------|--------------|
| `s3_revisions_bucket` | Entity revision snapshots | 4.0.0 | JSON (hash keys) |
| `s3_statements_bucket` | Deduplicated statements | 1.0.0 | JSON |
| `s3_references_bucket` | Deduplicated references | 1.0.0 | JSON |
| `s3_qualifiers_bucket` | Deduplicated qualifiers | 1.0.0 | JSON |
| `s3_snaks_bucket` | Deduplicated snaks | 1.0.0 | JSON |
| `s3_terms_bucket` | Deduplicated terms (labels/descriptions/aliases) | - | UTF-8 text |
| `s3_sitelinks_bucket` | Deduplicated sitelink titles | - | UTF-8 text |
| `s3_lexeme_forms_bucket` | Deduplicated lexeme form representations | - | JSON |
| `s3_lexeme_senses_bucket` | Deduplicated lexeme sense glosses | - | JSON |

### S3 Object Paths

**Revisions** (content_hash-based):
```
s3://wikibase-revisions/{content_hash}.json
Example: s3://wikibase-revisions/123456789012345.json
```

**Statements**:
```
s3://wikibase-statements/{content_hash}.json
```

**References**:
```
s3://wikibase-references/{content_hash}.json
```

**Qualifiers**:
```
s3://wikibase-qualifiers/{content_hash}.json
```

**Snaks**:
```
s3://wikibase-snaks/{content_hash}.json
```

**Terms** (UTF-8 text):
```
s3://wikibase-terms/{content_hash}
```

**Sitelinks** (UTF-8 text):
```
s3://wikibase-sitelinks/{content_hash}
```

**Lexeme Forms**:
```
s3://wikibase-lexeme-forms/{content_hash}.json
```

**Lexeme Senses**:
```
s3://wikibase-lexeme-senses/{content_hash}.json
```

### Revision Schema 4.0.0

Revision data stored in S3 as JSON:

```json
{
  "schema_version": "4.0.0",
  "entity": {
    "id": "Q123",
    "type": "item"
  },
  "labels_hashes": {"en": 123456789, "de": 234567890},
  "descriptions_hashes": {"en": 345678901},
  "aliases_hashes": {"en": [456789012, 567890123]},
  "sitelinks_hashes": {"enwiki": 678901234},
  "statements_hashes": {"P31": [789012345], "P569": [890123456]},
  "redirects_to": "Q124"
}
```

**Key Features:**
- All content uses hash integer references (not inline objects)
- Enables efficient deduplication across revisions
- Reduces storage by ~90% through content sharing
- Hash-based keys ideal for CDN caching

---

## 3.2 Vitess Storage - Metadata and Indexing

Vitess stores **pointers, metadata, and relationships**, never entity content.

### Database Tables

#### Entity Tables

**entity_head** - Current state of each entity
```sql
CREATE TABLE entity_head (
    entity_id VARCHAR(50) PRIMARY KEY,
    head_revision_id BIGINT UNSIGNED NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;
```

**entity_revisions** - Revision metadata
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
    INDEX idx_created_at (created_at)
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

#### ID Generation

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

#### Statement Deduplication

**statement_content** - Deduplicated statements
```sql
CREATE TABLE statement_content (
    content_hash BIGINT UNSIGNED PRIMARY KEY,
    ref_count BIGINT UNSIGNED NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_ref_count (ref_count)
) ENGINE=InnoDB;
```

#### Lexeme Tables

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

#### User and Social Features

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

#### Statistics Tables

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

#### Metadata Tables

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
   - Hash and deduplicate statements
   - Hash and deduplicate references/qualifiers/snaks
   - Hash terms (labels/descriptions/aliases)
   - Hash sitelinks
   - Store unique content to S3
  ↓
4. Assign next revision_id (auto-increment in entity_revisions)
  ↓
5. Write revision snapshot to S3 with content_hash as key
  ↓
6. Insert revision metadata into Vitess (entity_revisions)
   - Store content_hash for retrieval
  ↓
7. CAS update entity_head (new revision becomes head)
  ↓
8. Update statement_content ref_counts
  ↓
9. Publish change event to Kafka (optional)
  ↓
10. Confirm ID usage (for entity creation)
  ↓
11. Commit transaction

On failure:
  - Rollback Vitess changes
  - Decrement ref_counts for orphaned content
  - Delete from S3 (for new content)
```

**Transaction Safety:**
- All Vitess operations wrapped in database transaction
- S3 operations tracked for rollback
- Ref counts decremented on rollback
- ID ranges only confirmed after successful commit

### 4.2 Read Flows

**GET /entities/{entity_id}**
```
1. Query entity_head for head_revision_id
2. Query entity_revisions for content_hash
3. Load revision from S3 using content_hash
4. Load all hash-referenced content:
   - Terms from s3_terms_bucket
   - Sitelinks from s3_sitelinks_bucket
   - Statements from s3_statements_bucket
   - References from s3_references_bucket
   - Qualifiers from s3_qualifiers_bucket
   - Snaks from s3_snaks_bucket
5. Reconstruct full entity response
6. Return JSON
```

**GET /entities/{entity_id}/revision/{revision_id}**
```
1. Query entity_revisions for content_hash
2. Load revision from S3 using content_hash
3. Load hash-referenced content (as above)
4. Return JSON
```

**GET /entities/{entity_id}/history**
```
1. Query entity_revisions for entity_id
2. Return list of revision metadata (no S3 load needed)
3. Response: revision_id, created_at, editor, edit_summary
```

**GET /statements/{hash}**
```
1. Check statement_content table exists and ref_count > 0
2. Load statement from S3
3. Return statement with reconstructed snaks
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

- **Statements**: Hash of mainsnak + qualifiers + references
- **References**: Hash of snaks array
- **Qualifiers**: Hash of snak hash array
- **Snaks**: Hash of property_id + datavalue
- **Terms**: Hash of language_code + value
- **Sitelinks**: Hash of title
- **Lexeme Forms**: Hash of representations hash array
- **Lexeme Senses**: Hash of glosses hash array

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
    # Delete from S3
    for hash in orphans:
        s3_client.delete_statement(hash)
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

All S3 content includes schema version for evolution:

| Schema | Version | Status | Notes |
|--------|---------|--------|-------|
| Entity (response) | 2.0.0 | Current | Hash-based references |
| Revision (storage) | 4.0.0 | Current | Full deduplication, hash keys |
| Statement | 1.0.0 | Current | Hash-referenced snaks |
| Reference | 1.0.0 | Current | Hash-referenced snaks |
| Qualifier | 1.0.0 | Current | Hash-referenced snaks |
| Snak | 1.0.0 | Current | Atomic datavalue |

**Migration**: See [S3-REVISION-SCHEMA-CHANGELOG.md](./S3/S3-REVISION-SCHEMA-CHANGELOG.md) for detailed migration history.

---

## 7. Performance Characteristics

### S3
- **Write latency**: ~100-300ms per PUT
- **Read latency**: ~50-200ms per GET
- **Throughput**: Unlimited (horizontal scaling)
- **CDN caching**: Enabled for all public buckets

### Vitess
- **Write latency**: ~10-50ms per transaction
- **Read latency**: ~5-20ms per query
- **Sharding**: Not currently implemented (single shard)
- **Connection pooling**: Configurable pool size

### Combined Read Path
- **Total latency**: ~200-500ms per entity read
- **Optimization**: Batch hash lookups reduce round-trips
- **Caching**: Entity responses cached in Redis (optional)

---

## 8. Data Integrity

### Transaction Safety
- All Vitess writes wrapped in ACID transactions
- S3 operations tracked for rollback
- Ref counts ensure consistency

### Hash Verification
- Content hash computed before storage
- Hash verified on retrieval (optional, for debugging)
- Rapidhash provides collision resistance

### Rollback Handling
```
On transaction failure:
1. Rollback Vitess transaction (automatic)
2. Decrement ref_counts for orphaned content
3. Delete from S3 (new content only)
4. Confirm ID usage failure (cancel reserved range)
```

---

## References

- [ENTITY-MODEL.md](./ENTITY-MODEL.md) - Entity ID strategy and models
- [REPOSITORIES.md](./REPOSITORIES.md) - Repository classes for data access
- [STATEMENT-DEDUPLICATION.md](./STATEMENT-DEDUPLICATION.md) - Statement deduplication details
- [S3-REVISION-ID-STRATEGY.md](./S3/S3-REVISION-ID-STRATEGY.md) - Revision ID strategy
- [S3-REVISION-SCHEMA-EVOLUTION.md](./S3/S3-REVISION-SCHEMA-EVOLUTION.md) - Schema evolution and migration
