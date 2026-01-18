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

- `get_protection_info(conn, entity_id) -> ProtectionResponse | None`
  - Get protection status information for an entity.

## Backlinks

### BacklinkRepository

**Location**: `models/infrastructure/vitess/backlink_repository.py`
**Purpose**: Repository for managing entity backlinks in Vitess.

**Methods**:

- `insert_backlinks(conn, backlinks) -> OperationResult`
  - Insert backlinks into entity_backlinks table.

        backlinks: list of (referenced_internal_id, referencing_internal_id, statement_hash, property_id, rank)

- `delete_backlinks_for_entity(conn, referencing_internal_id) -> OperationResult`
  - Delete all backlinks for a referencing entity (used for updates).

- `get_backlinks(conn, referenced_internal_id, limit, offset) -> list[BacklinkEntry]`
  - Get backlinks for an entity.

- `insert_backlink_statistics(conn, date, total_backlinks, unique_entities_with_backlinks, top_entities_by_backlinks) -> None`
  - Insert daily backlink statistics.

        Args:
            conn: Database connection
            date: Date string in ISO format (YYYY-MM-DD)
            total_backlinks: Total number of backlinks
            unique_entities_with_backlinks: Number of unique entities with backlinks
            top_entities_by_backlinks: List of top entities by backlink count

        Raises:
            ValueError: If input validation fails
            Exception: If database operation fails

## Statements

### StatementRepository

**Location**: `models/infrastructure/vitess/statement_repository.py`
**Purpose**: Repository for statement-related database operations.

**Methods**:

- `insert_content(conn, content_hash) -> OperationResult`
  - Insert statement content hash if it doesn't exist.

- `increment_ref_count(conn, content_hash) -> OperationResult`
  - Increment reference count for statement content.

- `decrement_ref_count(conn, content_hash) -> OperationResult`
  - Decrement reference count for statement content.

- `get_orphaned(conn, older_than_days, limit) -> OperationResult`
  - Get orphaned statement content hashes.

- `get_most_used(conn, limit, min_ref_count) -> list[int]`
  - Get most used statement content hashes.

- `get_ref_count(conn, content_hash) -> int`
  - Get the reference count for a statement.

- `delete_content(conn, content_hash) -> None`
  - Delete statement content when ref_count reaches 0.

- `get_all_statement_hashes(conn) -> list[int]`
  - Get all statement content hashes.

## Metadata

### MetadataRepository

**Location**: `models/infrastructure/vitess/metadata_repository.py`
**Purpose**: Repository for metadata content operations.

**Methods**:

- `insert_metadata_content(conn, content_hash, content_type) -> OperationResult`
  - Insert or increment ref_count for metadata content.

- `get_metadata_content(conn, content_hash, content_type) -> OperationResult`
  - Get metadata content by hash and type.

- `decrement_ref_count(conn, content_hash, content_type) -> OperationResult`
  - Decrement ref_count and return True if it reaches 0.

- `delete_metadata_content(conn, content_hash, content_type) -> None`
  - Delete metadata content when ref_count reaches 0.

## Other

### EndorsementRepository

**Location**: `models/infrastructure/vitess/endorsement_repository.py`
**Purpose**: Repository for managing statement endorsements in Vitess.

**Methods**:

- `create_endorsement(user_id, statement_hash) -> OperationResult`
  - Create an endorsement for a statement.

- `withdraw_endorsement(user_id, statement_hash) -> OperationResult`
  - Withdraw an endorsement for a statement.

- `get_statement_endorsements(statement_hash, limit, offset, include_removed) -> OperationResult`
  - Get all endorsements for a statement.

- `get_user_endorsements(user_id, limit, offset, include_removed) -> OperationResult`
  - Get endorsements given by a user.

- `get_user_endorsement_stats(user_id) -> OperationResult`
  - Get endorsement statistics for a user.

- `get_batch_statement_endorsement_stats(statement_hashes) -> OperationResult`
  - Get endorsement statistics for multiple statements.

### HeadRepository

**Location**: `models/infrastructure/vitess/head_repository.py`
**Purpose**: Repository for entity head revision database operations.

**Methods**:

- `cas_update_with_status(conn, entity_id, expected_head, new_head, is_semi_protected, is_locked, is_archived, is_dangling, is_mass_edit_protected, is_deleted, is_redirect) -> OperationResult`
  - Update entity head with compare-and-swap semantics and status flags.

- `hard_delete(conn, entity_id, head_revision_id) -> OperationResult`
  - Mark an entity as hard deleted.

- `soft_delete(conn, entity_id) -> OperationResult`
  - Mark an entity as soft deleted.

- `get_head_revision(internal_entity_id) -> OperationResult`
  - Get the current head revision for an entity by internal ID.

### ListingRepository

**Location**: `models/infrastructure/vitess/listing_repository.py`
**Purpose**: Repository for entity listing operations.

**Methods**:

- `list_locked(conn, limit) -> list[EntityListing]`

- `list_semi_protected(conn, limit) -> list[EntityListing]`

- `list_archived(conn, limit) -> list[EntityListing]`

- `list_dangling(conn, limit) -> list[EntityListing]`

### RedirectRepository

**Location**: `models/infrastructure/vitess/redirect_repository.py`
**Purpose**: Repository for entity redirect database operations.

**Methods**:

- `set_target(conn, entity_id, redirects_to_entity_id, expected_redirects_to) -> OperationResult`
  - Set redirect target for an entity.

- `create(conn, redirect_from_entity_id, redirect_to_entity_id, created_by) -> None`
  - Create a redirect from one entity to another.

- `get_incoming_redirects(conn, entity_id) -> list[str]`
  - Get entities that redirect to the given entity.

- `get_target(conn, entity_id) -> str`
  - Get the redirect target for an entity.

### RevisionRepository

**Location**: `models/infrastructure/vitess/revision_repository.py`
**Purpose**: Repository for entity revision database operations.

**Methods**:

- `insert(conn, entity_id, revision_id, data) -> None`
  - Insert a new revision for an entity.

- `get_revision(internal_entity_id, revision_id, vitess_client) -> Any | None`
  - Get a specific revision data.

- `revert_entity(internal_entity_id, to_revision_id, reverted_by_user_id, reason, watchlist_context, vitess_client) -> int`
  - Revert entity to a previous revision and log the action.

- `get_history(conn, entity_id, limit, offset) -> list[Any]`
  - Get revision history for an entity.

- `delete(conn, entity_id, revision_id) -> OperationResult`
  - Delete a revision (for rollback).

- `create_with_cas(conn, entity_id, revision_id, data, expected_revision_id) -> bool`
  - Create a revision with compare-and-swap semantics.

- `create(conn, entity_id, revision_id, data) -> None`
  - Create a new revision for an entity.

### TermsRepository

**Location**: `models/infrastructure/vitess/terms_repository.py`
**Purpose**: Repository for managing deduplicated terms (labels and aliases) in Vitess.

**Methods**:

- `insert_term(hash_value, term, term_type) -> OperationResult`
  - Insert a term if it doesn't already exist.

- `get_term(hash_value) -> tuple[str, str] | None`
  - Retrieve a term and its type by hash.

- `batch_get_terms(hashes) -> TermsResponse`
  - Retrieve multiple terms by their hashes.

- `hash_exists(hash_value) -> bool`
  - Check if a hash exists in the terms table.

### ThanksRepository

**Location**: `models/infrastructure/vitess/thanks_repository.py`
**Purpose**: Repository for managing thanks in Vitess.

**Methods**:

- `send_thank(from_user_id, entity_id, revision_id) -> OperationResult`
  - Send a thank for a revision.

- `get_thanks_received(user_id, hours, limit, offset) -> OperationResult`
  - Get thanks received by user.

- `get_thanks_sent(user_id, hours, limit, offset) -> OperationResult`
  - Get thanks sent by user.

- `get_revision_thanks(entity_id, revision_id) -> OperationResult`
  - Get all thanks for a specific revision.

### UserRepository

**Location**: `models/infrastructure/vitess/user_repository.py`
**Purpose**: Repository for managing users in Vitess.

**Methods**:

- `create_user(user_id) -> OperationResult`
  - Create a new user record if it does not exist (idempotent).

        Inserts a user into the users table. If the user already exists, the operation
        succeeds without changes due to the ON DUPLICATE KEY clause.

        Args:
            user_id: The unique ID of the user to create. Must be positive.

        Returns:
            OperationResult: Indicates success or failure. On success, success=True.
                On failure (e.g., database error), success=False with an error message.

- `user_exists(user_id) -> bool`
  - Check if a user exists in the database.

        Queries the users table to determine if a record exists for the given user ID.

        Args:
            user_id: The ID of the user to check.

        Returns:
            bool: True if the user exists, False otherwise.

- `get_user(user_id) -> User | None`
  - Get user data by ID.

- `update_user_activity(user_id) -> OperationResult`
  - Update user's last activity timestamp.

- `is_watchlist_enabled(user_id) -> bool`
  - Check if watchlist is enabled for user.

- `set_watchlist_enabled(user_id, enabled) -> OperationResult`
  - Enable or disable watchlist for user.

- `disable_watchlist(user_id) -> OperationResult`
  - Disable watchlist for user (idempotent).

- `log_user_activity(user_id, activity_type, entity_id, revision_id) -> OperationResult`
  - Log a user activity for tracking interactions with entities.

        Inserts a record into the user_activity table to record user actions
        such as edits, views, or other interactions on entities.

        Args:
            user_id: The ID of the user performing the activity. Must be positive.
            activity_type: A string describing the type of activity (e.g., 'edit', 'view').
            entity_id: The ID of the entity involved in the activity (e.g., 'Q42').
            revision_id: The revision ID associated with the activity. Defaults to 0,
                indicating no specific revision (e.g., for non-edit activities like views).
                Pass the actual revision ID for revision-specific actions.

        Returns:
            OperationResult: Indicates success or failure of the logging operation.
                On success, success=True. On failure, success=False with an error message.

        Note:
            Basic validation is performed on user_id and activity_type before insertion.
            Database errors (e.g., connection issues) are caught and returned as failures.

- `get_user_preferences(user_id) -> OperationResult`
  - Get user notification preferences.

- `update_user_preferences(notification_limit, retention_hours, user_id) -> OperationResult`
  - Update user notification preferences.

- `get_user_activities(user_id, activity_type, hours, limit, offset) -> OperationResult`
  - Get user's activities with filtering.

- `insert_general_statistics(conn, date, total_statements, total_qualifiers, total_references, total_items, total_lexemes, total_properties, total_sitelinks, total_terms, terms_per_language, terms_by_type) -> None`
  - Insert daily general statistics.

        Args:
            conn: Database connection
            date: Date string in ISO format (YYYY-MM-DD)
            total_statements: Total statements
            total_qualifiers: Total qualifiers
            total_references: Total references
            total_items: Total items
            total_lexemes: Total lexemes
            total_properties: Total properties
            total_sitelinks: Total sitelinks
            total_terms: Total terms
            terms_per_language: Terms per language dict
            terms_by_type: Terms by type dict

        Raises:
            ValueError: If input validation fails
            Exception: If database operation fails

- `insert_user_statistics(conn, date, total_users, active_users) -> None`
  - Insert daily user statistics.

        Args:
            conn: Database connection
            date: Date string in ISO format (YYYY-MM-DD)
            total_users: Total number of users
            active_users: Number of active users

        Raises:
            ValueError: If input validation fails
            Exception: If database operation fails

### WatchlistRepository

**Location**: `models/infrastructure/vitess/watchlist_repository.py`
**Purpose**: Repository for managing watchlists in Vitess.

**Methods**:

- `get_entity_watch_count(user_id) -> int`
  - Get count of entity watches (whole entity, no properties) for user.

- `get_property_watch_count(user_id) -> int`
  - Get count of entity-property watches (with properties) for user.

- `add_watch(user_id, entity_id, properties) -> OperationResult`
  - Add a watchlist entry.

- `remove_watch(user_id, entity_id, properties) -> None`
  - Remove a watchlist entry.

- `get_watches_for_user(user_id) -> List[Any]`
  - Get all watchlist entries for a user.

- `get_watchers_for_entity(entity_id) -> List[Any]`
  - Get all watchers for an entity (for notifications).

- `get_notification_count(user_id) -> int`
  - Get count of active notifications for user.

- `get_user_notifications(user_id, hours, limit, offset) -> List[Any]`
  - Get recent notifications for a user within time span.

- `mark_notification_checked(notification_id, user_id) -> None`
  - Mark a notification as checked.

## Architecture Notes

- **Connection Management**: All repositories receive a `connection_manager` for database access
- **Transaction Safety**: Methods should be called within connection contexts
- **Error Handling**: Repositories raise exceptions for database errors
- **Performance**: Methods are optimized for common query patterns
- **Data Integrity**: Foreign key relationships are maintained at the application level

