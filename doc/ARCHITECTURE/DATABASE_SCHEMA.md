# Database Schema Overview

This document describes Vitess database schema used by wikibase-backend.

## Summary

- **Total Tables**: 17
- **Database**: MySQL (via Vitess)
- **Schema File**: `src/models/infrastructure/vitess/repositories/schema.py`

---

## Entity Tables

### entity_id_mapping
Maps external entity IDs (e.g., Q123) to internal IDs (BIGINT).

**Columns**:
- `entity_id` (VARCHAR(50)): External entity ID (PRIMARY KEY)
- `internal_id` (BIGINT UNSIGNED): Internal ID (UNIQUE)

**Location**: `src/models/infrastructure/vitess/repositories/schema.py`

---

### entity_head
Tracks current state of each entity including head revision ID and protection flags.

**Columns**:
- `internal_id` (BIGINT UNSIGNED): Internal entity ID (PRIMARY KEY)
- `head_revision_id` (BIGINT): Current head revision ID
- `is_semi_protected` (BOOLEAN): Whether entity is semi-protected
- `is_locked` (BOOLEAN): Whether entity is locked
- `is_archived` (BOOLEAN): Whether entity is archived
- `is_dangling` (BOOLEAN): Whether entity is dangling
- `is_mass_edit_protected` (BOOLEAN): Whether entity is mass edit protected
- `is_deleted` (BOOLEAN): Whether entity is deleted
- `is_redirect` (BOOLEAN): Whether entity is a redirect
- `redirects_to` (BIGINT UNSIGNED): Internal ID this redirects to (if applicable)

**Location**: `src/models/infrastructure/vitess/repositories/schema.py`

---

### entity_revisions
Stores revision metadata for entities.

**Columns**:
- `internal_id` (BIGINT UNSIGNED): Internal entity ID
- `revision_id` (BIGINT): Revision number
- `created_at` (TIMESTAMP): Creation timestamp (PRIMARY KEY part 1)
- `is_mass_edit` (BOOLEAN): Whether revision is a mass edit
- `edit_type` (VARCHAR(100)): Type of edit
- `statements` (JSON): Statement hashes
- `properties` (JSON): Property hashes
- `property_counts` (JSON): Count of properties
- `labels_hashes` (JSON): Label hashes
- `descriptions_hashes` (JSON): Description hashes
- `aliases_hashes` (JSON): Alias hashes
- `sitelinks_hashes` (JSON): Sitelink hashes
- `user_id` (BIGINT UNSIGNED): User ID who created revision
- `edit_summary` (TEXT): Edit summary
- `content_hash` (BIGINT UNSIGNED): Hash of full revision content

**Location**: `src/models/infrastructure/vitess/repositories/schema.py`

---

### entity_redirects
Tracks entity redirects.

**Columns**:
- `id` (BIGINT): Redirect ID (PRIMARY KEY, AUTO_INCREMENT)
- `redirect_from_id` (BIGINT UNSIGNED): Internal ID being redirected from
- `redirect_to_id` (BIGINT UNSIGNED): Internal ID being redirected to
- `created_at` (TIMESTAMP): Creation timestamp
- `created_by` (VARCHAR(255)): User who created redirect

**Indexes**:
- `idx_redirect_from` (redirect_from_id)
- `idx_redirect_to` (redirect_to_id)
- `unique_redirect` (redirect_from_id, redirect_to_id) - UNIQUE

**Location**: `src/models/infrastructure/vitess/repositories/schema.py`

---

### entity_backlinks
Tracks which entities reference other entities via statements.

**Columns**:
- `referenced_internal_id` (BIGINT UNSIGNED): Internal ID of referenced entity (PRIMARY KEY part 1)
- `referencing_internal_id` (BIGINT UNSIGNED): Internal ID of referencing entity (PRIMARY KEY part 2)
- `statement_hash` (BIGINT UNSIGNED): Hash of statement (PRIMARY KEY part 3)
- `rank` (ENUM): Preferred, normal, or deprecated (PRIMARY KEY part 4)

**Foreign Keys**:
- `referenced_internal_id` → `entity_id_mapping(internal_id)`
- `referencing_internal_id` → `entity_id_mapping(internal_id)`
- `statement_hash` → `statement_content(content_hash)`

**Indexes**:
- `idx_backlinks_property` (referencing_internal_id, property_id)

**Location**: `src/models/infrastructure/vitess/repositories/schema.py`

---

### entity_terms
Stores term text labels and aliases with deduplication.

**Columns**:
- `hash` (BIGINT): Hash of term text (PRIMARY KEY)
- `term` (TEXT): Term text content
- `term_type` (ENUM): Type of term (label, alias)
- `created_at` (TIMESTAMP): Creation timestamp

**Location**: `src/models/infrastructure/vitess/repositories/schema.py`

---

### metadata_content
Stores metadata content (labels, descriptions, aliases) with reference counting.

**Columns**:
- `content_hash` (BIGINT UNSIGNED): Hash of content (PRIMARY KEY part 1)
- `content_type` (ENUM): Type of content (labels, descriptions, aliases) (PRIMARY KEY part 2)
- `created_at` (TIMESTAMP): Creation timestamp
- `ref_count` (INT): Reference count

**Indexes**:
- `idx_type_hash` (content_type, content_hash)
- `idx_ref_count` (ref_count DESC)

**Location**: `src/models/infrastructure/vitess/repositories/schema.py`

---

### statement_content
Deduplicated statement storage with reference counting.

**Columns**:
- `content_hash` (BIGINT UNSIGNED): Hash of statement content (PRIMARY KEY)
- `created_at` (TIMESTAMP): Creation timestamp
- `ref_count` (INT): Number of entities using this statement

**Indexes**:
- `idx_ref_count` (ref_count DESC)

**Location**: `src/models/infrastructure/vitess/repositories/schema.py`

---

### lexeme_terms
Stores lexeme form and sense representations with deduplication.

**Columns**:
- `entity_id` (VARCHAR(20)): Lexeme entity ID (PRIMARY KEY part 1)
- `form_sense_id` (VARCHAR(20)): Form or sense ID (PRIMARY KEY part 2)
- `term_type` (ENUM): Type of term (form, sense) (PRIMARY KEY part 3)
- `language` (VARCHAR(10)): Language code (PRIMARY KEY part 4)
- `term_hash` (BIGINT UNSIGNED): Hash of term content
- `created_at` (TIMESTAMP): Creation timestamp

**Indexes**:
- `idx_entity` (entity_id)
- `idx_hash` (term_hash)
- `idx_language` (language)

**Location**: `src/models/infrastructure/vitess/repositories/schema.py`

---

## User Tables

### users
Stores user information and preferences.

**Columns**:
- `user_id` (BIGINT): User ID (PRIMARY KEY)
- `created_at` (TIMESTAMP): Account creation timestamp
- `preferences` (JSON): User preferences
- `watchlist_enabled` (BOOLEAN): Whether watchlist is enabled
- `last_activity` (TIMESTAMP): Last activity timestamp
- `notification_limit` (INT): Maximum notifications to retain
- `retention_hours` (INT): Notification retention period

**Location**: `src/models/infrastructure/vitess/repositories/schema.py`

---

### watchlist
Tracks entities users are watching.

**Columns**:
- `id` (BIGINT): Watchlist entry ID (PRIMARY KEY, AUTO_INCREMENT)
- `user_id` (BIGINT): User ID watching
- `internal_entity_id` (BIGINT UNSIGNED): Internal entity ID being watched
- `watched_properties` (TEXT): Properties to watch
- `created_at` (TIMESTAMP): Creation timestamp

**Foreign Keys**:
- `internal_entity_id` → `entity_id_mapping(internal_id)`

**Indexes**:
- `unique_watch` (user_id, internal_entity_id, watched_properties(255)) - UNIQUE

**Location**: `src/models/infrastructure/vitess/repositories/schema.py`

---

### user_notifications
Stores notifications for user watchlist.

**Columns**:
- `id` (BIGINT): Notification ID (PRIMARY KEY, AUTO_INCREMENT)
- `user_id` (BIGINT): User ID receiving notification
- `entity_id` (VARCHAR(50)): External entity ID
- `revision_id` (BIGINT): Revision ID of change
- `change_type` (VARCHAR(50)): Type of change
- `changed_properties` (JSON): Properties that changed
- `event_timestamp` (TIMESTAMP): When the change occurred
- `is_checked` (BOOLEAN): Whether notification has been checked
- `checked_at` (TIMESTAMP): When notification was checked
- `created_at` (TIMESTAMP): Notification creation timestamp

**Indexes**:
- `idx_user_timestamp` (user_id, event_timestamp)
- `idx_entity` (entity_id)

**Location**: `src/models/infrastructure/vitess/repositories/schema.py`

---

### user_activity
Tracks user activity events.

**Columns**:
- `id` (BIGINT): Activity ID (PRIMARY KEY, AUTO_INCREMENT)
- `user_id` (BIGINT): User ID
- `activity_type` (VARCHAR(50)): Type of activity
- `entity_id` (VARCHAR(50)): External entity ID (if applicable)
- `revision_id` (BIGINT): Revision ID (if applicable)
- `created_at` (TIMESTAMP): Activity timestamp

**Indexes**:
- `idx_user_type_time` (user_id, activity_type, created_at)
- `idx_entity` (entity_id)

**Location**: `src/models/infrastructure/vitess/repositories/schema.py`

---

### user_thanks
Stores thanks between users.

**Columns**:
- `id` (BIGINT): Thank ID (PRIMARY KEY, AUTO_INCREMENT)
- `from_user_id` (BIGINT): User ID sending thanks
- `to_user_id` (BIGINT): User ID receiving thanks
- `internal_entity_id` (BIGINT UNSIGNED): Internal entity ID
- `revision_id` (BIGINT): Revision ID
- `created_at` (TIMESTAMP): Creation timestamp

**Foreign Keys**:
- `internal_entity_id` → `entity_id_mapping(internal_id)`

**Indexes**:
- `idx_from_user` (from_user_id, created_at)
- `idx_to_user` (to_user_id, created_at)
- `idx_revision` (internal_entity_id, revision_id)
- `unique_thank` (from_user_id, internal_entity_id, revision_id) - UNIQUE

**Location**: `src/models/infrastructure/vitess/repositories/schema.py`

---

### user_statement_endorsements
Stores user endorsements for statements.

**Columns**:
- `id` (BIGINT): Endorsement ID (PRIMARY KEY, AUTO_INCREMENT)
- `user_id` (BIGINT): User ID endorsing
- `statement_hash` (BIGINT UNSIGNED): Hash of endorsed statement
- `created_at` (TIMESTAMP): Creation timestamp
- `removed_at` (TIMESTAMP): Timestamp when endorsement was removed

**Foreign Keys**:
- `statement_hash` → `statement_content(content_hash)`

**Indexes**:
- `idx_user` (user_id, created_at)
- `idx_statement` (statement_hash, created_at)
- `idx_removed` (removed_at)
- `unique_endorsement` (user_id, statement_hash) - UNIQUE

**Location**: `src/models/infrastructure/vitess/repositories/schema.py`

---

## Statistics Tables

### backlink_statistics
Aggregated backlink statistics computed by background worker.

**Columns**:
- `date` (DATE): Statistics date (PRIMARY KEY)
- `total_backlinks` (BIGINT): Total number of backlinks
- `unique_entities_with_backlinks` (BIGINT): Number of unique entities with backlinks
- `top_entities_by_backlinks` (JSON): Top N entities by backlink count
- `created_at` (TIMESTAMP): Computation timestamp

**Location**: `src/models/infrastructure/vitess/repositories/schema.py`

---

### user_daily_stats
Daily user statistics computed by background worker.

**Columns**:
- `stat_date` (DATE): Statistics date (PRIMARY KEY)
- `total_users` (BIGINT): Total number of users
- `active_users` (BIGINT): Number of active users (last 30 days)
- `created_at` (TIMESTAMP): Computation timestamp

**Location**: `src/models/infrastructure/vitess/repositories/schema.py`

---

### general_daily_stats
Daily general wiki statistics computed by background worker.

**Columns**:
- `stat_date` (DATE): Statistics date (PRIMARY KEY)
- `total_statements` (BIGINT): Total number of statements
- `total_qualifiers` (BIGINT): Total number of qualifiers
- `total_references` (BIGINT): Total number of references
- `total_items` (BIGINT): Total number of items
- `total_lexemes` (BIGINT): Total number of lexemes
- `total_properties` (BIGINT): Total number of properties
- `total_sitelinks` (BIGINT): Total number of sitelinks
- `total_terms` (BIGINT): Total number of terms
- `terms_per_language` (JSON): Terms breakdown by language
- `terms_by_type` (JSON): Terms breakdown by type
- `created_at` (TIMESTAMP): Computation timestamp

**Location**: `src/models/infrastructure/vitess/repositories/schema.py`

---

## ID Management Tables

### id_ranges
Manages ID range allocation for entity ID generation.

**Columns**:
- `entity_type` (VARCHAR(1)): Entity type (Q, P, L, E) (PRIMARY KEY)
- `current_range_start` (BIGINT UNSIGNED): Start of current reserved range
- `current_range_end` (BIGINT UNSIGNED): End of current reserved range
- `range_size` (BIGINT UNSIGNED): Size of ID ranges
- `allocated_at` (TIMESTAMP): When range was allocated
- `worker_id` (VARCHAR(64)): ID of worker that allocated range
- `version` (BIGINT): Allocation version

**Location**: `src/models/infrastructure/vitess/repositories/schema.py`

---

## Entity Relationship Diagram

```mermaid
erDiagram
    users ||--o{ watchlist : watches
    users ||--o{ user_notifications : receives
    users ||--o{ user_activity : performs
    users ||--o{ user_thanks : sends
    users ||--o{ user_statement_endorsements : endorses
    watchlist }|--|| entity_id_mapping : references
    user_notifications }--|| entity_id_mapping : references
    user_activity }--|| entity_id_mapping : references
    user_thanks }--|| entity_id_mapping : references
    entity_head ||--o{ entity_revisions : tracks
    entity_id_mapping ||--o{ entity_head : has
    entity_id_mapping ||--o{ entity_redirects : redirects_from
    entity_id_mapping ||--o{ entity_redirects : redirects_to
    entity_id_mapping ||--o{ entity_backlinks : referenced_by
    entity_id_mapping ||--o{ entity_backlinks : references
    entity_backlinks }|--|| statement_content : contains
    user_statement_endorsements }|--|| statement_content : endorses
    lexeme_terms ||--o{ entity_id_mapping : belongs_to
```

---

## Notes

- **Entity ID Strategy**: External entity IDs (Q123, P42, L999) are mapped to internal BIGINT IDs via `entity_id_mapping` table
- **ID Range Generation**: `id_ranges` table manages pre-allocated ranges for high-throughput ID generation
- **Deduplication**: Statements, terms, and metadata use hash-based deduplication with reference counting
- **Reference Counting**: Content with `ref_count = 0` can be safely deleted (orphaned content cleanup)
- **Protection Flags**: `entity_head` stores various protection flags (semi-protected, locked, archived, etc.)
- **Foreign Keys**: Foreign key relationships are enforced at application level via `entity_id_mapping`
- **Indexes**: All tables have indexes optimized for common query patterns
- **Initialization**: Schema is created automatically via `SchemaRepository.create_tables()` method
- **BIGINT Types**: All ID fields use BIGINT UNSIGNED for Vitess compatibility and scalability

---

## Related Documentation

- [STORAGE-ARCHITECTURE.md](./STORAGE-ARCHITECTURE.md) - S3 and Vitess storage design
- [REPOSITORIES.md](./REPOSITORIES.md) - Repository classes for data access
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Overall system architecture
- [ENTITY-MODEL.md](./ENTITY-MODEL.md) - Entity ID strategy and models
