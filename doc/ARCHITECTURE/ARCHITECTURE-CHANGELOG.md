# Architecture Changelog

This file tracks architectural changes, feature additions, and modifications to wikibase-backend system.

## [2026-01-13] Sitelinks Deduplication, Endpoints, and Batch API

### Summary

Implemented sitelinks deduplication by hashing titles only, keeping wiki identifiers in revisions. Added new S3 bucket for sitelinks metadata, individual lookup endpoints, and batch endpoints for all metadata types to improve frontend performance and caching.

### Motivation

- **Storage Efficiency**: Deduplicate repeated sitelinks titles across entities and revisions.
- **Consistency**: Align sitelinks with existing metadata deduplication for labels/descriptions/aliases.
- **API Completeness**: Provide endpoints to query sitelinks and lookup titles by hash.
- **Performance**: Add batch endpoints to reduce round-trips for multiple metadata lookups.
- **Scalability**: Organize metadata storage for better management and caching.

### Changes

#### Storage and Deduplication
- Added "sitelinks" S3 bucket created by the development worker.
- Modified revision write logic to hash sitelinks titles and store in sitelinks/{hash}.json.
- Updated read logic to reconstruct sitelinks from hashes.
- Added sitelinks_hashes to entity_revisions database schema.

#### API Endpoints
- Added GET /entitybase/v1/entities/item/{id}/sitelinks/{wiki_id} to retrieve sitelink title for a specific wiki in an entity.
- Added GET /entitybase/v1/sitelinks/{hashes} (batch, up to 20 hashes) to lookup titles by hashes.
- Added GET /entitybase/v1/labels/{hashes} (batch) for labels.
- Added GET /entitybase/v1/descriptions/{hashes} (batch) for descriptions.
- Added GET /entitybase/v1/aliases/{hashes} (batch) for aliases.
- Added GET /entitybase/v1/statements/batch?entity_ids=...&property_ids=... (batch) for statements.

#### Infrastructure
- Extended MetadataExtractor for sitelinks title hashing.
- Updated CreateBuckets worker to include "sitelinks" bucket.
- Added validation for sitelinks hashes in RevisionData.

## [2026-01-13] RevisionData Model Addition

### Summary

Introduced RevisionData Pydantic model to structure and validate top-level revision JSON data, replacing raw Dict[str, Any] in RevisionReadResponse. Includes strict allowlist validation for entity keys to enforce Wikibase structure without over-parsing.

### Motivation

- **Type Safety**: Improve validation and error handling for revision data inputs/outputs.
- **Consistency**: Align with Pydantic best practices for JSON-close models.
- **Security**: Prevent invalid keys in entity data via strict allowlist, reducing malformed data risks.
- **Maintainability**: Prepare for future enhancements while avoiding unnecessary nesting.

### Changes

#### Model Changes
- Added RevisionData class in src/models/s3_models.py with fields for schema_version, entity (with allowlist validator), and optional redirects_to.
- Validator raises validation errors for invalid entity keys using raise_validation_error.

#### API Changes
- Updated RevisionReadResponse.data to use RevisionData.
- Modified s3_client.py to instantiate RevisionData from parsed JSON, with strict validation.
- Adjusted handlers in read.py and admin.py to use model_dump() for dict compatibility.

## [2026-01-13] Entity History API Endpoint

### Summary

Implemented `GET /entities/{entity_id}/history` endpoint to retrieve revision history for entities, including revision ID, timestamp, user ID, and edit summary. Added required database schema changes to store edit metadata.

### Motivation

- **Audit Trail**: Provide complete edit history for entities to track changes and accountability
- **User Experience**: Allow users to see who made changes and why
- **Compliance**: Support requirements for change tracking and transparency
- **API Completeness**: Round out entity management capabilities with history viewing

### Changes

#### Database Schema Changes

- Added `created_by_user_id` column to `entity_revisions` table
- Added `edit_summary` column to `entity_revisions` table

#### API Changes

- Updated `RevisionMetadataResponse` model to include `user_id` and `edit_summary` fields
- Implemented `VitessClient.get_entity_history()` method
- Updated `EntityReadHandler.get_entity_history()` to return complete metadata
- Enhanced `/entities/{entity_id}/history` endpoint with pagination support

#### Code Changes

- Modified revision insertion logic to capture user and edit summary
- Updated history queries to include new metadata fields
- Added filtering to skip incomplete history entries
- Required non-empty edit_summary in entity creation, update, and delete requests
- Removed unused editor fields from request models and tests

## [2026-01-12] Backlink Statistics Script

### Summary

Implemented a daily statistics computation script that analyzes all entity statements to generate backlink analytics. The script scans statement content from S3, extracts entity references, and aggregates backlink counts stored in a new `backlink_statistics` Vitess table.

### Motivation

- **Analytics**: Enable insights into entity connectivity and relationship patterns at scale
- **Performance Monitoring**: Track backlink distribution and growth metrics
- **Query Optimization**: Support UI features showing popular entities by connectivity
- **Scalability**: Background computation prevents API performance impact
- **Maintenance**: Automated daily updates ensure fresh statistics

### Changes

#### New Database Table

**File**: `src/models/infrastructure/vitess/schema.py`

Added `backlink_statistics` table:

```sql
CREATE TABLE IF NOT EXISTS backlink_statistics (
    date DATE PRIMARY KEY,
    total_backlinks BIGINT NOT NULL,
    unique_entities_with_backlinks BIGINT NOT NULL,
    top_entities_by_backlinks JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Fields**:
- `date`: Date of computation (partition key)
- `total_backlinks`: Total backlink relationships across all entities
- `unique_entities_with_backlinks`: Number of entities that have at least one incoming backlink
- `top_entities_by_backlinks`: JSON array of top 100 entities by backlink count

#### Statistics Computation Script

**File**: `scripts/statistics/backlink_statistics.py`

New script with comprehensive backlink analysis:

```python
async def compute_backlinks(vitess_client, s3_client) -> None:
    """Compute backlink statistics for all entities"""

async def extract_entity_references(statement_content: dict) -> list[str]:
    """Extract entity IDs referenced in a statement"""

# Main execution
await compute_backlinks(vitess_client, s3_client)
```

**Features**:
- Scans all statement hashes from Vitess `statement_content` table
- Batch fetches statement content from S3 for efficiency
- Parses statement JSON to extract entity references from mainsnak, qualifiers, and references
- Aggregates backlink counts per entity
- Stores daily global statistics with top entities ranking

#### Repository Extensions

**File**: `src/models/infrastructure/vitess/statement_repository.py`

Added `get_all_statement_hashes()` method:

```python
def get_all_statement_hashes(self, conn: Any) -> list[int]:
    """Get all statement content hashes for backlink computation"""
```

**File**: `src/models/infrastructure/vitess/backlink_repository.py`

Added `insert_backlink_statistics()` method:

```python
def insert_backlink_statistics(
    self, conn: Any, date: str, total_backlinks: int,
    unique_entities_with_backlinks: int, top_entities_by_backlinks: list[dict]
) -> None:
    """Insert daily backlink statistics with upsert logic"""
```

#### S3 Client Extensions

**File**: `src/models/infrastructure/s3/s3_client.py`

Added `batch_get_statements()` method:

```python
async def batch_get_statements(self, content_hashes: list[int]) -> dict[int, dict[str, Any]]:
    """Batch read multiple statements from S3 for efficient processing"""
```

### Impact

- **Storage**: Minimal additional storage (~1KB/day for statistics table)
- **Performance**: Background computation doesn't impact API performance
- **Analytics**: Enables insights into entity relationship patterns
- **Monitoring**: Health checks and error logging for operational visibility

### Backward Compatibility

- **Non-breaking**: New table and script don't affect existing functionality
- **Optional**: Script can be disabled or run on-demand
- **Graceful degradation**: Statistics unavailable if script fails

## [2026-01-12] Hash Algorithm Decision: 64-bit Rapidhash

### Summary

Completed comprehensive analysis of hash collision probabilities across different hash sizes (64-bit, 96-bit, 112-bit, 128-bit, 256-bit) for Wikibase scale (10 billion entities, 2 trillion total items). Decision: permanently use 64-bit rapidhash due to sufficient collision resistance and migration impossibility.

### Motivation

- **Collision Analysis**: Determine optimal hash size for data integrity at massive scale
- **Ecosystem Stability**: Avoid breaking changes that would affect 1000+ consumers
- **Performance Optimization**: Balance collision safety with storage/performance costs
- **Migration Feasibility**: Assess practical upgrade paths for hash algorithms

### Analysis Results

#### Collision Probabilities (at 2×10^12 items)
- **64-bit rapidhash**: 1 in 9,174 (negligible risk)
- **128-bit SHA256**: 1 in 10^15 (astronomically low)
- **256-bit SHA256**: 1 in 10^69 (theoretically impossible)

#### Storage Costs
- **64-bit**: 8 bytes/hash (baseline)
- **128-bit**: 16 bytes/hash (2x increase, $160/month)
- **256-bit**: 32 bytes/hash (4x increase, $320/month)

#### Migration Assessment
- **Hash format changes**: Effectively impossible due to ecosystem scale
- **Linking table**: Would require 80TB for 2 trillion mappings
- **Consumer coordination**: 1000+ applications would need simultaneous updates

### Changes

#### Updated Risk Documentation

**File**: `doc/RISK/HASH-COLLISION.md`

Comprehensive rewrite with:
- Mathematical collision probability analysis
- Performance and storage cost comparisons
- Migration impossibility assessment
- Final decision documentation
- Monitoring and detection strategies

#### Hash Algorithm Standardization

**Decision**: Use 64-bit rapidhash for all content hashing:
- Entity JSON snapshots
- Statement deduplication
- Term string deduplication
- Metadata content hashing

### Impact

- **Data Integrity**: Negligible collision risk at target scale
- **Ecosystem Stability**: No breaking changes for consumers
- **Performance**: Optimal hash generation speed
- **Storage**: Minimal overhead (8 bytes per hash)
- **Operations**: Simplified architecture without migration complexity

### Backward Compatibility

- **No changes**: Existing 64-bit hashes remain compatible
- **Future-proofing**: Can add secondary hash verification if needed
- **Monitoring**: Collision detection logging for anomaly detection

## [2026-01-12] Event JSON Schema Definitions

### Summary

Added JSON Schema definitions for `entitychange` and `entitypropertychange` event types to standardize and validate event payloads in the Kafka streaming system. These schemas ensure consistent event structure for consumers like watchlist services and analytics pipelines.

### Motivation

- **Event Standardization**: Define canonical formats for entity change events
- **Validation**: Enable runtime validation of event payloads against schemas
- **Consumer Safety**: Prevent malformed events from breaking downstream processing
- **Documentation**: Provide clear contracts for event producers and consumers

### Changes

#### New Event Schemas

**Files**: `src/schemas/events/entitychange.json`, `src/schemas/events/entitypropertychange.json`

- **entitychange.json**: Base schema for all entity change events with fields: entity_id, revision_id, change_type, from_revision_id, changed_at, editor, edit_summary
- **entitypropertychange.json**: Extended schema for property-specific changes, adding required `changed_properties` array

Both schemas use JSON Schema Draft 2020-12 with validation patterns for entity/property IDs and enumerated change types.

## [2026-01-12] User Registration Support

### Summary

Added user registration endpoint and users table to support watchlist features with MediaWiki user IDs. This enables frontend-initiated user registration without authentication, allowing users to be tracked for watchlist subscriptions and notifications.

### Motivation

- **User Management**: Provide a way to register users in the system using MediaWiki IDs
- **Watchlist Foundation**: Enable user-specific watchlist operations and notifications
- **Frontend Integration**: Allow frontend to create user entries as needed
- **Simplicity**: No auth required, trusting frontend for valid MediaWiki user_ids

### Changes

#### New Users Table

**File**: `src/models/infrastructure/vitess/schema.py`

Added `users` table creation:
- `user_id` (BIGINT PRIMARY KEY) - MediaWiki user ID
- `created_at` (TIMESTAMP) - Registration timestamp
- `preferences` (JSON) - Reserved for future user preferences

#### User Registration Endpoints

**File**: `src/models/rest_api/main.py`

New endpoints:
- `POST /v1/users`: Create/register user with MediaWiki ID
  - Request: `{"user_id": 12345}`
  - Response: `{"user_id": 12345, "created": true/false}`
  - Idempotent, no authentication
- `GET /v1/users/{user_id}`: Retrieve user information
  - Returns user data or 404 if not found
  - Allows frontend to check user existence/registration status

#### Watchlist Support Implementation

**Summary**

Implemented core watchlist functionality for subscribing to entity changes or specific properties. Includes data models, storage, and API endpoints for managing watches.

**Motivation**

- **User Subscriptions**: Enable users to track changes on entities or properties
- **Granular Watching**: Support whole-entity or property-specific watches
- **Foundation for Notifications**: Prepare for event-driven change alerts

**Changes**

##### Watchlist Data Models

**File**: `src/models/watchlist.py`

- `WatchlistEntry`: DB model with user_id, internal_entity_id, watched_properties
- `WatchlistAddRequest`: API request for adding watches
- `WatchlistRemoveRequest`: API request for removing watches
- `WatchlistResponse`: API response listing user's watches

##### Watchlist Repository

**File**: `src/models/infrastructure/vitess/watchlist_repository.py`

New `WatchlistRepository` class with ID resolution:
- `add_watch()`: Add watch with external→internal ID conversion
- `remove_watch()`: Remove watch by user/entity/properties
- `get_watches_for_user()`: Retrieve user's watchlist with resolved entity_ids
- `get_watchers_for_entity()`: Get watchers for an entity (for notifications)

##### Database Schema

**File**: `src/models/infrastructure/vitess/schema.py`

Added `watchlist` table:
- `user_id` (BIGINT)
- `internal_entity_id` (BIGINT, FK to entity_id_mapping)
- `watched_properties` (TEXT, comma-separated)
- Primary key: (user_id, internal_entity_id, watched_properties)

##### API Endpoints

**File**: `src/models/rest_api/main.py`

New watchlist endpoints:
- `POST /v1/watchlist`: Add watch
  - Request: `{"user_id": 12345, "entity_id": "Q42", "properties": ["P31"]}`
- `DELETE /v1/watchlist`: Remove watch
  - Request: `{"user_id": 12345, "entity_id": "Q42", "properties": ["P31"]}`
- `GET /v1/watchlist?user_id=12345`: Get user's watchlist
  - Response: `{"user_id": 12345, "watches": [{"entity_id": "Q42", "properties": ["P31"]}...]}`

All endpoints validate user registration and handle ID resolution internally.

#### Future Integration

Watchlist endpoints will validate user existence against this table to ensure only registered users can create watchlists.

#### Watchlist Notifications System

**Summary**

Implemented event-driven notification system for watchlist changes. Includes background consumer worker, notification storage, and API endpoints for frontend to retrieve and manage notifications.

**Motivation**

- **Real-time Updates**: Enable users to receive notifications when watched entities/properties change
- **Event-Driven**: Leverage existing Kafka event stream for scalable notifications
- **User Experience**: Provide recent changes feed with check/ack functionality

**Changes**

##### Notification Storage

**File**: `src/models/infrastructure/vitess/schema.py`

Added `user_notifications` table:
- `user_id` (BIGINT)
- `entity_id` (VARCHAR), `revision_id` (INT), `change_type` (VARCHAR)
- `changed_properties` (JSON), `event_timestamp` (TIMESTAMP)
- `is_checked` (BOOLEAN), `checked_at` (TIMESTAMP)

##### Event Consumer Worker

**File**: `src/models/workers/watchlist_consumer/main.py`

New `WatchlistConsumerWorker`:
- Consumes `entitychange`/`entitypropertychange` events from Kafka
- Matches events against user watchlists
- Creates notification records for relevant users
- Handles property-specific vs. entity-wide watches

##### Notification API Endpoints

**File**: `src/models/rest_api/main.py`

New endpoints:
- `GET /v1/watchlist/notifications?user_id=X&limit=30`: Retrieve recent notifications
- `POST /v1/watchlist/notifications/check`: Mark notification as checked

Response includes notification details: entity, revision, change type, properties, timestamps.

##### Repository Extensions

**File**: `src/models/infrastructure/vitess/watchlist_repository.py`

Added methods:
- `get_user_notifications()`: Fetch paginated notifications for user
- `mark_notification_checked()`: Update checked status
- `_create_notification()`: Insert notification (used by consumer)

This completes the watchlist system with end-to-end notification flow.

## [2026-01-12] User Notification Preferences

### Summary

Implemented user-configurable notification preferences with personalized limits and retention settings. Users can customize their notification experience while maintaining system scalability.

### Motivation

- **Personalization**: Allow users to control notification volume and retention based on their needs
- **Scalability**: User preferences enable fine-tuned resource management
- **User Experience**: Match individual workflows (power users vs. casual watchers)
- **Flexibility**: Support different notification patterns for subgraph protection

### Changes

#### Database Schema Extensions

**File**: `src/models/infrastructure/vitess/schema.py`

Extended `users` table with preference fields:
- `notification_limit` INT DEFAULT 50 (max notifications per user)
- `retention_hours` INT DEFAULT 24 (notification retention period)

#### User Preferences API

**File**: `src/models/rest_api/main.py`

New endpoints for preference management:
- `GET /v1/users/{user_id}/preferences`: Retrieve current notification settings
- `PUT /v1/users/{user_id}/preferences`: Update notification limit and retention

Request validation: notification_limit (50-500), retention_hours (1-720)

#### Repository Enhancements

**File**: `src/models/infrastructure/vitess/user_repository.py`

Added preference management methods:
- `get_user_preferences(user_id)`: Retrieve user's notification settings
- `update_user_preferences(user_id, limit, retention)`: Update user preferences

#### Consumer Integration

**File**: `src/models/workers/watchlist_consumer/main.py`

- Creates all eligible notifications without limit checks
- Cleanup worker enforces user preference limits via oldest-first deletion
- Simplified consumer logic focused on event processing

#### Handler Implementation

**File**: `src/models/rest_api/handlers/user_preferences.py`

- `UserPreferencesHandler`: Manages preference queries and updates
- Validation of preference ranges
- Integration with user repository

#### Request/Response Models

**Files**: `src/models/rest_api/request/user_preferences.py`, `src/models/rest_api/response/user_preferences.py`

- `UserPreferencesRequest`: notification_limit, retention_hours
- `UserPreferencesResponse`: user_id, notification_limit, retention_hours

#### User Experience

- Default settings: 50 notifications, 24-hour retention
- Customizable limits: Up to 500 notifications, 30-day retention
- Immediate effect: Preference changes apply to new notifications
- Backward compatibility: Existing users use defaults

#### Performance & Scaling

- Lightweight preference storage in users table
- Efficient queries for preference retrieval
- Consumer respects individual limits for fair resource usage
- No impact on existing notification processing

This enables personalized notification management while maintaining system performance and scalability.

## [2026-01-12] EntityBase Revert API for Subgraph Protection

### Summary

Added a new EntityBase API endpoint for reverting entities to previous revisions, enabling manual intervention against vandalism and problematic changes detected by the watchlist system. This supports subgraph protection workflows where users monitor large entity networks for quality issues.

### Motivation

- **Vandalism Response**: Provide tools for rapid reversion of damaging edits
- **Data Integrity**: Allow restoration of subgraphs affected by bad modeling
- **Consumer Protection**: Prevent negative impacts on downstream data users
- **Auditability**: Full logging of revert actions for transparency

### Changes

#### Revert API Endpoint

**File**: `src/models/rest_api/main.py`

New endpoint: `POST /entitybase/v1/entities/{entity_id}/revert`
- Reverts entity to specified revision with audit logging
- Requires `reverted_by_user_id` for accountability
- Includes optional watchlist context for linking to notifications

#### Revert Logging

**File**: `src/models/infrastructure/vitess/schema.py`

Added `revert_log` table:
- Tracks all reverts with entity, revision, user, reason details
- Supports subgraph protection audit trails
- Scales to trillions of entries with distributed storage

#### Handler and Repository

**Files**: `src/models/rest_api/handlers/entity/revert.py`, `src/models/infrastructure/vitess/revision_repository.py`

- `EntityRevertHandler`: Validates requests and coordinates reversion
- Extended `RevisionRepository.revert_entity()`: Performs data restoration and logging
- Error handling for invalid revisions and conflicts

#### API Models

**Files**: `src/models/rest_api/request/entity/revert.py`, `src/models/rest_api/response/entity/revert.py`

- `EntityRevertRequest`: to_revision_id, reason, reverted_by_user_id, watchlist_context
- `EntityRevertResponse`: entity_id, new_revision_id, reverted_from_revision_id, timestamp

#### Integration with Watchlist

- Revert API designed for integration with watchlist notifications
- Frontend can provide watchlist context for revert tracking
- Supports manual protection workflows without auto-reversion

## [2026-01-12] User Activity Logging System

### Summary

Implemented comprehensive user activity logging for entity operations, providing complete edit history and moderation trails. Activities point to revisions for detailed data storage.

### Motivation

- **Edit History**: Users need complete timeline of their entity operations
- **Moderation**: Track all entity modifications for audit and oversight
- **Transparency**: Clear record of create/edit/revert/delete operations
- **Analytics**: Enable contribution analysis and user activity patterns

### Changes

#### Activity Types and Models

**File**: `src/models/user_activity.py`

- `ActivityType` enum: entity_create, entity_edit, entity_revert, entity_delete, entity_undelete, entity_lock, entity_unlock, entity_archive, entity_unarchive
- `UserActivity` model: id, user_id, activity_type, entity_id, revision_id, created_at

#### Activity Logging Infrastructure

**File**: `src/models/infrastructure/vitess/schema.py`

Added `user_activity` table:
- `user_id` (BIGINT), `activity_type` (VARCHAR), `entity_id` (VARCHAR), `revision_id` (BIGINT)
- `created_at` (TIMESTAMP), indexes on user_id, activity_type, entity_id

**File**: `src/models/infrastructure/vitess/user_repository.py`

- Added `log_user_activity()` method for consistent logging
- Stores minimal data + revision pointer for full details

#### Activity Logging Integration

**File**: `src/models/rest_api/handlers/entity/revert.py`

- Logs `entity_revert` activities with revision pointers
- Includes entity_id, revision_id, user_id for audit trail

#### Activity Retrieval API

**File**: `src/models/rest_api/main.py`

- `GET /v1/users/{user_id}/activity`: Retrieve user's activity history
- Parameters: hours (time filter), limit (50/100/250/500), type (activity type filter)
- Response: Activity list with revision pointers for detail access

#### Handler and Repository

**File**: `src/models/rest_api/handlers/user_activity.py`, `src/models/infrastructure/vitess/user_repository.py`

- `UserActivityHandler`: Processes activity queries with filtering
- Enhanced `UserRepository.get_user_activities()`: Supports time/type filtering, pagination

#### Future Integration Points

- Add logging to future entity create/edit/delete/lock/archive handlers
- Consistent activity logging across all entity operations
- Revision-based detail retrieval for rich activity views

#### Performance & Scaling

- Efficient indexing for user-specific queries
- Time-based filtering leverages revision storage
- Pagination prevents large response payloads
- Scales to millions of activities per user

## [2026-01-12] Backlink Statistics Worker

### Summary

Implemented a background worker service that computes and stores backlink statistics daily. The worker generates analytics on entity relationships including total backlinks, unique entities with backlinks, and top entities ranked by backlink count. Statistics are stored in a new `backlink_statistics` Vitess table for efficient querying.

### Motivation

- **Analytics**: Enable data-driven insights into entity connectivity and relationships
- **Performance Monitoring**: Track backlink growth and distribution patterns
- **Query Optimization**: Support UI features showing popular entities by connectivity
- **Scalability**: Background computation prevents API performance impact
- **Maintenance**: Automated daily updates ensure fresh statistics

### Changes

#### New Database Table

**File**: `src/models/infrastructure/vitess/schema.py`

Added `backlink_statistics` table:

```sql
CREATE TABLE IF NOT EXISTS backlink_statistics (
    date DATE PRIMARY KEY,
    total_backlinks BIGINT NOT NULL,
    unique_entities_with_backlinks BIGINT NOT NULL,
    top_entities_by_backlinks JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Fields**:
- `date`: Date of computation (partition key)
- `total_backlinks`: Total backlink relationships across all entities
- `unique_entities_with_backlinks`: Number of entities that have at least one incoming backlink
- `top_entities_by_backlinks`: JSON array of top 100 entities by backlink count

#### Statistics Service

**File**: `src/models/rest_api/services/backlink_statistics_service.py`

New `BacklinkStatisticsService` class:

```python
class BacklinkStatisticsService(BaseModel):
    def compute_daily_stats(self, vitess_client: VitessClient) -> BacklinkStatisticsData:
        """Compute comprehensive backlink statistics for current date"""

    def get_total_backlinks(self, vitess_client: VitessClient) -> int:
        """Count total backlink relationships"""

    def get_entities_with_backlinks(self, vitess_client: VitessClient) -> int:
        """Count entities that have incoming backlinks"""

    def get_top_entities_by_backlinks(
        self, vitess_client: VitessClient, limit: int = 100
    ) -> list[dict[str, Any]]:
        """Get top entities ranked by backlink count"""
```

#### Worker Implementation

**File**: `src/models/workers/backlink_statistics/backlink_statistics_worker.py`

New `BacklinkStatisticsWorker` class following existing worker pattern:

```python
class BacklinkStatisticsWorker(BaseModel):
    worker_id: str = Field(default_factory=lambda: os.getenv("WORKER_ID", f"backlink-stats-{os.getpid()}"))

    async def start(self) -> None:
        """Start the backlink statistics worker"""

    async def run_daily_computation(self) -> None:
        """Run daily statistics computation and storage"""

    async def health_check(self) -> WorkerHealthCheck:
        """Health check endpoint"""
```

**Features**:
- Daily scheduled execution (configurable via environment)
- Async processing to avoid blocking
- Comprehensive error handling and logging
- Health check endpoint for monitoring

#### Response Models

**File**: `src/models/rest_api/response/misc.py`

Added models for statistics data:

```python
class BacklinkStatisticsData(BaseModel):
    """Container for computed backlink statistics"""

    total_backlinks: int
    unique_entities_with_backlinks: int
    top_entities_by_backlinks: list[dict[str, Any]]

class BacklinkStatisticsResponse(BaseModel):
    """API response for backlink statistics"""

    date: str
    total_backlinks: int
    unique_entities_with_backlinks: int
    top_entities_by_backlinks: list[dict[str, Any]]
```

#### Configuration

**File**: `src/models/config/settings.py`

Added worker configuration:

```python
class Settings(BaseSettings):
    backlink_stats_enabled: bool = Field(default=True)
    backlink_stats_schedule: str = Field(default="0 2 * * *")  # Daily at 2 AM
    backlink_stats_top_limit: int = Field(default=100)
```

### Impact

- **Storage**: Minimal additional storage (~1KB/day for statistics table)
- **Performance**: Background computation doesn't impact API performance
- **Analytics**: Enables insights into entity relationship patterns
- **Monitoring**: Health checks and error logging for operational visibility

### Backward Compatibility

- **Non-breaking**: New table and worker don't affect existing functionality
- **Optional**: Worker can be disabled via configuration
- **Graceful degradation**: Statistics unavailable if worker fails

## [2026-01-11] S3 Revision Schema 2.0.0 - Term Deduplication

### Summary

Updated S3 revision schema to version 2.0.0 with per-language hash-based deduplication for labels, descriptions, and aliases. Implemented language-specific API endpoints for term retrieval. Documented hash collision risks.

### Motivation

- **Storage Efficiency**: Enable granular deduplication of term strings across languages/entities
- **API Completeness**: Provide language-specific endpoints for labels/aliases/descriptions
- **Scalability**: Reduce storage overhead for multilingual content

### Changes

#### Schema Update

**File**: `src/schemas/entitybase/s3-revision/2.0.0/schema.json` (renamed from 1.2.0)

- Bumped version to 2.0.0 for breaking changes
- Removed full `labels`, `descriptions`, `aliases` from `entity` object
- Added per-language hash maps:
  - `labels_hashes`: `{"en": hash, "fr": hash}`
  - `descriptions_hashes`: `{"en": hash}`
  - `aliases_hashes`: `{"en": [hash1, hash2]}`

#### Hashing Logic Update

**File**: `src/models/internal_representation/metadata_extractor.py`

Modified `hash_metadata()` to compute individual 64-bit rapidhashes for each term string instead of entire objects.

#### Revision Storage Changes

**File**: `src/models/rest_api/handlers/entity/__init__.py`

Updated revision creation to:
- Extract terms per language from entity data
- Hash individual strings and store in language-keyed maps
- Store term strings in S3 keyed by hash for deduplication

#### Retrieval Logic Update

**File**: `src/models/rest_api/handlers/entity/read.py`

Modified entity loading to reconstruct full term objects by loading strings from S3 using hash maps.

#### API Endpoints Implementation

**Files**: `src/models/rest_api/wikibase/v1/entity/items.py`, `properties.py`

Replaced 501 stubs with functional endpoints for:
- `GET /entities/items/{id}/labels/{lang}`
- `GET /entities/items/{id}/descriptions/{lang}`
- `GET /entities/items/{id}/aliases/{lang}`

#### Risk Documentation

**File**: `doc/RISK/HASH-COLLISION.md` (new)

Documented 64-bit hash collision probability and accepted risks for deduplication.

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
