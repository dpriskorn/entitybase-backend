# Database Schema Overview

This document describes the Vitess database schema used by wikibase-backend.

## Summary

- **Total Tables**: 14
- **Database**: MySQL (via Vitess)
- **Schema File**: `src/models/infrastructure/vitess/schema.py`

## Tables

### entity_id_mapping

**Columns**:

- `entity_id`: VARCHAR(50

**SQL Definition**:

```sql
CREATE TABLE IF NOT EXISTS entity_id_mapping ( entity_id VARCHAR(50) PRIMARY KEY, internal_id BIGINT NOT NULL UNIQUE )
```

### entity_head

**Columns**:

- `head_revision_id`: BIGINT NOT NULL
- `is_semi_protected`: BOOLEAN DEFAULT FALSE
- `is_locked`: BOOLEAN DEFAULT FALSE
- `is_archived`: BOOLEAN DEFAULT FALSE
- `is_dangling`: BOOLEAN DEFAULT FALSE
- `is_mass_edit_protected`: BOOLEAN DEFAULT FALSE
- `is_deleted`: BOOLEAN DEFAULT FALSE
- `is_redirect`: BOOLEAN DEFAULT FALSE
- `redirects_to`: BIGINT NULL

**SQL Definition**:

```sql
CREATE TABLE IF NOT EXISTS entity_head ( internal_id BIGINT PRIMARY KEY, head_revision_id BIGINT NOT NULL, is_semi_protected BOOLEAN DEFAULT FALSE, is_locked BOOLEAN DEFAULT FALSE, is_archived BOOLEAN DEFAULT FALSE, is_dangling BOOLEAN DEFAULT FALSE, is_mass_edit_protected BOOLEAN DEFAULT FALSE, is_deleted BOOLEAN DEFAULT FALSE, is_redirect BOOLEAN DEFAULT FALSE, redirects_to BIGINT NULL )
```

### entity_redirects

**Columns**:

- `redirect_from_id`: BIGINT NOT NULL
- `redirect_to_id`: BIGINT NOT NULL
- `created_at`: TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
- `created_by`: VARCHAR(255

**SQL Definition**:

```sql
CREATE TABLE IF NOT EXISTS entity_redirects ( id BIGINT PRIMARY KEY AUTO_INCREMENT, redirect_from_id BIGINT NOT NULL, redirect_to_id BIGINT NOT NULL, created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, created_by VARCHAR(255) DEFAULT NULL, INDEX idx_redirect_from (redirect_from_id), INDEX idx_redirect_to (redirect_to_id), UNIQUE KEY unique_redirect (redirect_from_id, redirect_to_id) )
```

### statement_content

**Columns**:

- `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- `ref_count`: INT DEFAULT 1

**SQL Definition**:

```sql
CREATE TABLE IF NOT EXISTS statement_content ( content_hash BIGINT UNSIGNED PRIMARY KEY, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, ref_count INT DEFAULT 1, INDEX idx_ref_count (ref_count DESC) )
```

### entity_backlinks

**Columns**:

- `referenced_internal_id`: BIGINT NOT NULL
- `referencing_internal_id`: BIGINT NOT NULL
- `statement_hash`: BIGINT UNSIGNED NOT NULL
- `property_id`: VARCHAR(32

**SQL Definition**:

```sql
CREATE TABLE IF NOT EXISTS entity_backlinks ( referenced_internal_id BIGINT NOT NULL, referencing_internal_id BIGINT NOT NULL, statement_hash BIGINT UNSIGNED NOT NULL, property_id VARCHAR(32) NOT NULL, `rank` ENUM('preferred', 'normal', 'deprecated') NOT NULL, PRIMARY KEY (referenced_internal_id, referencing_internal_id, statement_hash), FOREIGN KEY (referenced_internal_id) REFERENCES entity_id_mapping(internal_id), FOREIGN KEY (referencing_internal_id) REFERENCES entity_id_mapping(internal_id), FOREIGN KEY (statement_hash) REFERENCES statement_content(content_hash), INDEX idx_backlinks_property (referencing_internal_id, property_id) )
```

### backlink_statistics

**Columns**:

- `total_backlinks`: BIGINT NOT NULL
- `unique_entities_with_backlinks`: BIGINT NOT NULL
- `top_entities_by_backlinks`: JSON NOT NULL
- `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

**SQL Definition**:

```sql
CREATE TABLE IF NOT EXISTS backlink_statistics ( date DATE PRIMARY KEY, total_backlinks BIGINT NOT NULL, unique_entities_with_backlinks BIGINT NOT NULL, top_entities_by_backlinks JSON NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP )
```

### metadata_content

**Columns**:

- `content_hash`: BIGINT UNSIGNED NOT NULL
- `content_type`: ENUM('labels'

**SQL Definition**:

```sql
CREATE TABLE IF NOT EXISTS metadata_content ( content_hash BIGINT UNSIGNED NOT NULL, content_type ENUM('labels', 'descriptions', 'aliases') NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, ref_count INT DEFAULT 1, PRIMARY KEY (content_hash, content_type), INDEX idx_type_hash (content_type, content_hash), INDEX idx_ref_count (ref_count DESC) )
```

### entity_revisions

**Columns**:

- `internal_id`: BIGINT NOT NULL
- `revision_id`: BIGINT NOT NULL
- `created_at`: TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
- `is_mass_edit`: BOOLEAN DEFAULT FALSE
- `edit_type`: VARCHAR(100

**SQL Definition**:

```sql
CREATE TABLE IF NOT EXISTS entity_revisions ( internal_id BIGINT NOT NULL, revision_id BIGINT NOT NULL, created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, is_mass_edit BOOLEAN DEFAULT FALSE, edit_type VARCHAR(100) DEFAULT '', statements JSON NOT NULL, properties JSON NOT NULL, property_counts JSON NOT NULL, labels_hashes JSON, descriptions_hashes JSON, aliases_hashes JSON, PRIMARY KEY (internal_id, revision_id) )
```

### entity_terms

**Columns**:

- `term`: TEXT NOT NULL
- `term_type`: ENUM('label'

**SQL Definition**:

```sql
CREATE TABLE IF NOT EXISTS entity_terms ( hash BIGINT PRIMARY KEY, term TEXT NOT NULL, term_type ENUM('label', 'alias') NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP )
```

### id_ranges

**Columns**:

- `entity_type`: VARCHAR(1

**SQL Definition**:

```sql
CREATE TABLE IF NOT EXISTS id_ranges ( entity_type VARCHAR(1) PRIMARY KEY, current_range_start BIGINT NOT NULL DEFAULT 1, current_range_end BIGINT NOT NULL DEFAULT 1000000, range_size BIGINT DEFAULT 1000000, allocated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, worker_id VARCHAR(64), version BIGINT DEFAULT 0 )
```

### users

**Columns**:

- `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- `preferences`: JSON DEFAULT NULL
- `watchlist_enabled`: BOOLEAN DEFAULT TRUE
- `last_activity`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- `notification_limit`: INT DEFAULT 50
- `retention_hours`: INT DEFAULT 24

**SQL Definition**:

```sql
CREATE TABLE IF NOT EXISTS users ( user_id BIGINT PRIMARY KEY, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, preferences JSON DEFAULT NULL, watchlist_enabled BOOLEAN DEFAULT TRUE, last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP, notification_limit INT DEFAULT 50, retention_hours INT DEFAULT 24 )
```

### watchlist

**Columns**:

- `user_id`: BIGINT NOT NULL
- `internal_entity_id`: BIGINT NOT NULL
- `watched_properties`: TEXT DEFAULT NULL
- `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP

**SQL Definition**:

```sql
CREATE TABLE IF NOT EXISTS watchlist ( user_id BIGINT NOT NULL, internal_entity_id BIGINT NOT NULL, watched_properties TEXT DEFAULT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (user_id, internal_entity_id, watched_properties(255)), FOREIGN KEY (internal_entity_id) REFERENCES entity_id_mapping(internal_id) )
```

### user_notifications

**Columns**:

- `user_id`: BIGINT NOT NULL
- `entity_id`: VARCHAR(50

**SQL Definition**:

```sql
CREATE TABLE IF NOT EXISTS user_notifications ( id BIGINT PRIMARY KEY AUTO_INCREMENT, user_id BIGINT NOT NULL, entity_id VARCHAR(50) NOT NULL, revision_id BIGINT NOT NULL, change_type VARCHAR(50) NOT NULL, changed_properties JSON DEFAULT NULL, event_timestamp TIMESTAMP NOT NULL, is_checked BOOLEAN DEFAULT FALSE, checked_at TIMESTAMP NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, INDEX idx_user_timestamp (user_id, event_timestamp), INDEX idx_entity (entity_id) )
```

### user_activity

**Columns**:

- `user_id`: BIGINT NOT NULL
- `activity_type`: VARCHAR(50

**SQL Definition**:

```sql
CREATE TABLE IF NOT EXISTS user_activity ( id BIGINT PRIMARY KEY AUTO_INCREMENT, user_id BIGINT NOT NULL, activity_type VARCHAR(50) NOT NULL, entity_id VARCHAR(50), revision_id BIGINT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, INDEX idx_user_type_time (user_id, activity_type, created_at), INDEX idx_entity (entity_id) )
```

## Entity Relationship Diagram

```mermaid
erDiagram
    entity_id_mapping {
        - `entity_id`: VARCHAR(50
    }
    entity_head {
        - `head_revision_id`: BIGINT NOT NULL
        - `is_semi_protected`: BOOLEAN DEFAULT FALSE
        - `is_locked`: BOOLEAN DEFAULT FALSE
        - `is_archived`: BOOLEAN DEFAULT FALSE
        - `is_dangling`: BOOLEAN DEFAULT FALSE
        ... (9 total columns)
    }
    entity_redirects {
        - `redirect_from_id`: BIGINT NOT NULL
        - `redirect_to_id`: BIGINT NOT NULL
        - `created_at`: TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        - `created_by`: VARCHAR(255
    }
    statement_content {
        - `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        - `ref_count`: INT DEFAULT 1
    }
    entity_backlinks {
        - `referenced_internal_id`: BIGINT NOT NULL
        - `referencing_internal_id`: BIGINT NOT NULL
        - `statement_hash`: BIGINT UNSIGNED NOT NULL
        - `property_id`: VARCHAR(32
    }
    backlink_statistics {
        - `total_backlinks`: BIGINT NOT NULL
        - `unique_entities_with_backlinks`: BIGINT NOT NULL
        - `top_entities_by_backlinks`: JSON NOT NULL
        - `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    }
    metadata_content {
        - `content_hash`: BIGINT UNSIGNED NOT NULL
        - `content_type`: ENUM('labels'
    }
    entity_revisions {
        - `internal_id`: BIGINT NOT NULL
        - `revision_id`: BIGINT NOT NULL
        - `created_at`: TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        - `is_mass_edit`: BOOLEAN DEFAULT FALSE
        - `edit_type`: VARCHAR(100
    }
    entity_terms {
        - `term`: TEXT NOT NULL
        - `term_type`: ENUM('label'
    }
    id_ranges {
        - `entity_type`: VARCHAR(1
    }
    users {
        - `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        - `preferences`: JSON DEFAULT NULL
        - `watchlist_enabled`: BOOLEAN DEFAULT TRUE
        - `last_activity`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        - `notification_limit`: INT DEFAULT 50
        ... (6 total columns)
    }
    watchlist {
        - `user_id`: BIGINT NOT NULL
        - `internal_entity_id`: BIGINT NOT NULL
        - `watched_properties`: TEXT DEFAULT NULL
        - `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    }
    user_notifications {
        - `user_id`: BIGINT NOT NULL
        - `entity_id`: VARCHAR(50
    }
    user_activity {
        - `user_id`: BIGINT NOT NULL
        - `activity_type`: VARCHAR(50
    }

    entity_backlinks ||--o{ entity_id_mapping : referenced_internal_id }
    entity_backlinks ||--o{ entity_id_mapping : referencing_internal_id }
    entity_backlinks ||--o{ statement_content : statement_hash }
    watchlist ||--o{ entity_id_mapping : internal_entity_id }
```

## Notes

- All tables use BIGINT primary keys for Vitess compatibility
- Foreign key relationships are enforced at the application level
- Indexes are optimized for the most common query patterns
- Schema is applied automatically during Vitess initialization
