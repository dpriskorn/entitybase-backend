# Repository Classes Overview

This document describes the repository classes that handle data access to Vitess.

## Core Entity Operations

### EntityRepository

**Location**: `models/infrastructure/vitess/entity_repository.py`
**Purpose**: Repository for entity-related database operations.

**Methods**:

- `get_head(conn, entity_id) -> int`
  - Get the current head revision ID for an entity.

- `is_deleted(conn, entity_id) -> bool`
  - Check if an entity is marked as deleted.

- `is_locked(conn, entity_id) -> bool`
  - Check if an entity is locked for editing.

- `is_archived(conn, entity_id) -> bool`
  - Check if an entity is archived.

- `get_protection_info(conn, entity_id) -> ProtectionInfo | None`
  - Get protection status information for an entity.

## Backlinks

### BacklinkRepository

**Location**: `models/infrastructure/vitess/backlink_repository.py`
**Purpose**: Repository for managing entity backlinks in Vitess.

**Methods**:

- `insert_backlinks(conn, backlinks) -> None`
  - Insert backlinks into entity_backlinks table.

        backlinks: list of (referenced_internal_id, referencing_internal_id, statement_hash, property_id, rank)

- `delete_backlinks_for_entity(conn, referencing_internal_id) -> None`
  - Delete all backlinks for a referencing entity (used for updates).

- `get_backlinks(conn, referenced_internal_id, limit, offset) -> list[BacklinkData]`
  - Get backlinks for an entity.

## Statements

### StatementRepository

**Location**: `models/infrastructure/vitess/statement_repository.py`
**Purpose**: Repository for statement-related database operations.

**Methods**:

- `insert_content(conn, content_hash) -> bool`
  - Insert statement content hash if it doesn't exist.

- `increment_ref_count(conn, content_hash) -> int`
  - Increment reference count for statement content.

- `decrement_ref_count(conn, content_hash) -> int`
  - Decrement reference count for statement content.

- `get_orphaned(conn, older_than_days, limit) -> list[int]`
  - Get orphaned statement content hashes.

- `get_most_used(conn, limit, min_ref_count) -> list[int]`
  - Get most used statement content hashes.

- `get_ref_count(conn, content_hash) -> int`
  - Get the reference count for a statement.

- `delete_content(conn, content_hash) -> None`
  - Delete statement content when ref_count reaches 0.

## Metadata

### MetadataRepository

**Location**: `models/infrastructure/vitess/metadata_repository.py`
**Purpose**: Repository for metadata content operations.

**Methods**:

- `insert_metadata_content(conn, content_hash, content_type) -> None`
  - Insert or increment ref_count for metadata content.

- `get_metadata_content(conn, content_hash, content_type) -> MetadataContent | None`
  - Get metadata content by hash and type.

- `decrement_ref_count(conn, content_hash, content_type) -> bool`
  - Decrement ref_count and return True if it reaches 0.

- `delete_metadata_content(conn, content_hash, content_type) -> None`
  - Delete metadata content when ref_count reaches 0.

## Other

### HeadRepository

**Location**: `models/infrastructure/vitess/head_repository.py`
**Purpose**: Repository for entity head revision database operations.

**Methods**:

- `cas_update_with_status(conn, entity_id, expected_head, new_head, is_semi_protected, is_locked, is_archived, is_dangling, is_mass_edit_protected, is_deleted, is_redirect) -> bool`
  - Update entity head with compare-and-swap semantics and status flags.

- `hard_delete(conn, entity_id, head_revision_id) -> None`
  - Mark an entity as hard deleted.

- `soft_delete(conn, entity_id) -> None`
  - Mark an entity as soft deleted.

### ListingRepository

**Location**: `models/infrastructure/vitess/listing_repository.py`
**Purpose**: Repository for entity listing operations.

### RedirectRepository

**Location**: `models/infrastructure/vitess/redirect_repository.py`
**Purpose**: Repository for entity redirect database operations.

**Methods**:

- `set_target(conn, entity_id, redirects_to_entity_id, expected_redirects_to) -> bool`
  - Set redirect target for an entity.

- `create(conn, redirect_from_entity_id, redirect_to_entity_id, created_by) -> None`
  - Create a redirect from one entity to another.

- `get_incoming_redirects(conn, entity_id) -> list[str]`
  - Get entities that redirect to the given entity.

- `get_target(conn, entity_id) -> str | None`
  - Get the redirect target for an entity.

### RevisionRepository

**Location**: `models/infrastructure/vitess/revision_repository.py`
**Purpose**: Repository for entity revision database operations.

**Methods**:

- `insert(conn, entity_id, revision_id, data) -> None`
  - Insert a new revision for an entity.

- `get_history(conn, entity_id, limit, offset) -> list[Any]`
  - Get revision history for an entity.

- `delete(conn, entity_id, revision_id) -> None`
  - Delete a revision (for rollback).

- `create_with_cas(conn, entity_id, revision_id, data, expected_revision_id) -> bool`
  - Create a revision with compare-and-swap semantics.

- `create(conn, entity_id, revision_id, data) -> None`
  - Create a new revision for an entity.

### TermsRepository

**Location**: `models/infrastructure/vitess/terms_repository.py`
**Purpose**: Repository for managing deduplicated terms (labels and aliases) in Vitess.

**Methods**:

- `insert_term(hash_value, term, term_type) -> None`
  - Insert a term if it doesn't already exist.

- `get_term(hash_value) -> tuple[str, str] | None`
  - Retrieve a term and its type by hash.

- `batch_get_terms(hashes) -> Dict[int, tuple[str, str]]`
  - Retrieve multiple terms by their hashes.

- `hash_exists(hash_value) -> bool`
  - Check if a hash exists in the terms table.

## Architecture Notes

- **Connection Management**: All repositories receive a `connection_manager` for database access
- **Transaction Safety**: Methods should be called within connection contexts
- **Error Handling**: Repositories raise exceptions for database errors
- **Performance**: Methods are optimized for common query patterns
- **Data Integrity**: Foreign key relationships are maintained at the application level

