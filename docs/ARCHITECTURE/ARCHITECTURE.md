# Wikibase Backend Architecture

Immutable Revision Architecture (Vitess + S3)

This document describes a clean-room, billion-scale Wikibase backend
architecture based on immutable S3 snapshots, Vitess indexing, and a
well-defined API boundary.

## Core invariant

**A revision is an immutable snapshot stored in S3.**
Once written, it never changes.

There are:
- No mutable revisions
- No diff storage
- No page-based state
- No MediaWiki-owned content

Everything else in the system derives from this rule.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  (Browser, Mobile Apps, SPARQL Queries, External Systems)        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    REST API Layer (FastAPI)                     │
│  - Entity CRUD endpoints                                        │
│  - Type-specific endpoints (items, properties, lexemes)        │
│  - Statement management                                          │
│  - User features (watchlist, thanks, endorsements)              │
│  - RDF export (Turtle, RDF XML, NTriples)                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     Service Layer                               │
│  - Entity operations (create, update, delete, revert)        │
│  - Statement deduplication                                      │
│  - Lexeme term processing                                       │
│  - User activity tracking                                       │
│  - Statistics computation                                        │
│  - RDF generation and diffing                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Repository Layer                             │
│  - VitessRepository (metadata, indexing)                       │
│  - S3Repository (immutable content)                             │
│  - StreamRepository (Kafka events)                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              Infrastructure Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │    S3        │  │   Vitess     │  │   Kafka      │         │
│  │  (Content)   │  │ (Metadata)   │  │ (Streaming)  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

## System Components

### 1. REST API Layer

**Main Application**: FastAPI application with async/await support

**API Version**: `/v1/entitybase` (configurable via `api_prefix`)

**Endpoint Categories**:

#### Entity CRUD
- `GET /entities/{entity_id}` - Get entity (JSON/TTL/RDF)
- `GET /entities/{entity_id}/history` - Get revision history
- `GET /entities/{entity_id}/revision/{revision_id}` - Get specific revision
- `DELETE /entities/{entity_id}` - Delete entity

#### Type-Specific Creation
- `POST /entities/items` - Create item (auto-assigns Q-ID)
- `POST /entities/properties` - Create property (auto-assigns P-ID)
- `POST /entities/lexemes` - Create lexeme (auto-assigns L-ID)
- `PUT /entities/items/{item_id}` - Update item
- `PUT /entities/properties/{property_id}` - Update property
- `PUT /entities/lexemes/{lexeme_id}` - Update lexeme

#### Statement Management
- `GET /entities/{entity_id}/properties` - List unique properties
- `GET /entities/{entity_id}/properties/{list}` - Get property hashes
- `POST /entities/{entity_id}/properties/{property_id}` - Add statements
- `DELETE /entities/{entity_id}/statements/{hash}` - Remove statement
- `PATCH /entities/{entity_id}/statements/{hash}` - Patch statement
- `GET /statements/{hash}` - Get statement by hash
- `POST /statements/batch` - Batch get statements
- `GET /statements/most_used` - Get most used statements
- `POST /statements/cleanup-orphaned` - Cleanup orphaned statements

#### Terms Management
- `GET /entities/items/{item_id}/labels/{lang}` - Get item label
- `PUT /entities/items/{item_id}/labels/{lang}` - Update item label
- `DELETE /entities/items/{item_id}/labels/{lang}` - Delete item label
- Similar for descriptions, aliases, and lexemes

#### Sitelinks
- `GET /entities/{entity_id}/sitelinks/{site}` - Get sitelink
- `POST /entities/{entity_id}/sitelinks/{site}` - Add sitelink
- `PUT /entities/{entity_id}/sitelinks/{site}` - Update sitelink
- `DELETE /entities/{entity_id}/sitelinks/{site}` - Delete sitelink

#### Redirects
- `POST /redirects` - Create redirect
- `POST /entities/{id}/revert-redirect` - Revert redirect

#### Revert
- `POST /entities/{entity_id}/revert` - Revert to previous revision

#### User Features
- `GET /users/{user_id}` - Get user info
- `GET /users/{user_id}/activity` - Get user activity
- `POST /users/{user_id}/watchlist` - Add to watchlist
- `GET /users/{user_id}/watchlist` - Get watchlist
- `POST /users/{user_id}/thank` - Send thank

#### Endorsements
- `POST /statements/{hash}/endorse` - Endorse statement
- `DELETE /statements/{hash}/endorse` - Withdraw endorsement
- `GET /statements/{hash}/endorsements` - Get endorsements

#### Statistics
- `GET /stats` - Get general statistics
- `GET /health` - Health check

**Documentation**: See [ENDPOINTS.md](../ENDPOINTS.md) for complete endpoint list.

### 2. Service Layer

#### Entity Services
- **EntityHandler**: Base handler for all entity operations
- **EntityCreateHandler**: Entity creation logic
- **EntityUpdateHandler**: Entity update logic
- **EntityDeleteHandler**: Entity deletion logic
- **RedirectHandler**: Redirect management
- **RevertHandler**: Revision revert logic

#### Statement Services
- **StatementService**: Statement deduplication and storage
- **StatementHandler**: Statement CRUD operations
- **SnakHandler**: Snak deduplication

#### Lexeme Services
- **LexemeHandler**: Lexeme CRUD operations
- **LexemeFormHandler**: Form management
- **LexemeSenseHandler**: Sense management

#### User Services
- **UserHandler**: User operations
- **ThanksHandler**: Thanks feature
- **EndorsementHandler**: Endorsement feature
- **WatchlistHandler**: Watchlist management
- **UserStatsService**: User statistics computation
- **GeneralStatsService**: General statistics computation

#### RDF Services
- **EntityConverter**: Convert entities to RDF
- **EntityDiffWorker**: Compute RDF diffs between revisions
- **RDFSerializer**: Serialize entities to RDF formats

#### ID Generation
- **EnumerationService**: Range-based ID allocation

### 3. Repository Layer

#### Vitess Repositories
- **EntityRepository**: Entity metadata
- **HeadRepository**: Head revision tracking
- **RevisionRepository**: Revision metadata
- **StatementRepository**: Statement content tracking
- **BacklinkRepository**: Backlink tracking
- **RedirectRepository**: Redirect management
- **UserRepository**: User data
- **ThanksRepository**: Thanks data
- **EndorsementRepository**: Endorsement data
- **WatchlistRepository**: Watchlist data
- **ListingRepository**: Entity listings
- **TermsRepository**: Term metadata
- **LexemeRepository**: Lexeme-specific operations
- **MetadataRepository**: Entity metadata (flags)

#### S3 Repositories
- **RevisionStorage**: Revision snapshots
- **StatementStorage**: Statement content
- **ReferenceStorage**: Reference content
- **QualifierStorage**: Qualifier content
- **SnakStorage**: Snak content
- **MetadataStorage**: Term and sitelink metadata
- **LexemeStorage**: Lexeme forms and senses

#### Stream Repositories
- **EntityChangeStreamProducer**: Publish entity change events
- **EntityDiffStreamProducer**: Publish RDF diff events
- **Consumer**: Kafka event consumer for watchlist

**Documentation**: See `REPOSITORIES.md` for detailed repository documentation.

### 4. Background Workers

#### ID Generation Worker
- **File**: `src/models/workers/id_generation/id_generation_worker.py`
- **Purpose**: Reserves ID ranges for high-throughput entity creation
- **Schedule**: Continuous (no scheduled interval)

#### Entity Diff Worker
- **File**: `src/models/workers/entity_diff/entity_diff_worker.py`
- **Purpose**: Computes RDF diffs between entity revisions
- **Output**: Streams to `wikibase.entity_diff` Kafka topic

#### Backlink Statistics Worker
- **File**: `src/models/workers/backlink_statistics/backlink_statistics_worker.py`
- **Purpose**: Computes backlink statistics for entities
- **Schedule**: Daily at 2 AM (`0 2 * * *`)

#### User Stats Worker
- **File**: `src/models/workers/user_stats/user_stats_worker.py`
- **Purpose**: Computes daily user statistics
- **Schedule**: Daily at 2 AM (`0 2 * * *`)

#### General Stats Worker
- **File**: `src/models/workers/general_stats/general_stats_worker.py`
- **Purpose**: Computes daily general wiki statistics
- **Schedule**: Daily at 2 AM (`0 2 * * *`)

#### Watchlist Consumer Worker
- **File**: `src/models/workers/watchlist_consumer/main.py`
- **Purpose**: Consumes entity change events, creates watchlist notifications
- **Consumes**: Kafka topic `entitybase.entity_change`

#### Notification Cleanup Worker
- **File**: `src/models/workers/notification_cleanup/main.py`
- **Purpose**: Cleans up old watchlist notifications
- **Schedule**: Configurable

#### Dev Worker
- **File**: `src/models/workers/dev/__main__.py`
- **Purpose**: Development tools (bucket creation, table creation)
- **Commands**: `create_buckets`, `create_tables`

**Documentation**: See `WORKERS.md` for detailed worker documentation.

### 5. Data Flow

#### Entity Creation Flow
```
Client
  ↓ POST /entities/items
API Handler (EntityCreateHandler)
  ↓ Validate JSON schema
EnumerationService
  ↓ Allocate next Q-ID (e.g., Q123)
CreationTransaction
  ↓ Process statements (hash, deduplicate, store to S3)
  ↓ Store terms (hash, store to S3)
  ↓ Store sitelinks (hash, store to S3)
  ↓ Create revision snapshot (hash, store to S3)
Vitess (within transaction)
  ↓ Insert entity_revisions record
  ↓ Update entity_head
  ↓ Update statement_content ref_counts
Stream (optional)
  ↓ Publish entity change event
Response
  ↓ Return entity_id and revision_id
```

#### Entity Read Flow
```
Client
  ↓ GET /entities/Q123
API Handler
  ↓ Query entity_head for head_revision_id
Vitess
  ↓ Get revision metadata (including content_hash)
S3
  ↓ Load revision by content_hash
  ↓ Load hash-referenced content:
    - Terms (labels, descriptions, aliases)
    - Sitelinks
    - Statements (with referenced snaks, qualifiers, references)
  ↓ Reconstruct full entity
Response
  ↓ Return entity JSON
```

#### Statement Deduplication Flow
```
Entity Create/Update
  ↓ Extract statements from request
StatementService.deduplicate_and_store_statements
  ↓ For each statement:
    - Hash statement content (mainsnak + qualifiers + references)
    - Check if exists in statement_content table
    - If new: store to S3, insert record (ref_count=1)
    - If exists: increment ref_count
  ↓ Replace statement with hash reference in entity
Revision Storage
  ↓ Store revision with statement_hashes array
```

### 6. Storage Architecture

#### S3 Storage
- **Revisions**: Immutable snapshots stored by content_hash
- **Statements**: Deduplicated, stored by hash
- **References**: Deduplicated, stored by hash
- **Qualifiers**: Deduplicated, stored by hash
- **Snaks**: Deduplicated, stored by hash
- **Terms**: Deduplicated, stored by hash (UTF-8 text)
- **Sitelinks**: Deduplicated, stored by hash (UTF-8 text)
- **Lexeme Forms**: Deduplicated, stored by hash
- **Lexeme Senses**: Deduplicated, stored by hash

**Schema Versions**:
- Entity: 2.0.0 (hash-based responses)
- Revision: 4.0.0 (full deduplication)
- Statement: 1.0.0 (hash-referenced snaks)

**Documentation**: See `STORAGE-ARCHITECTURE.md` for complete storage architecture.

#### Vitess Storage
- **Entity metadata**: entity_head, entity_revisions, metadata
- **Statement tracking**: statement_content (hash + ref_count)
- **ID allocation**: id_ranges
- **User features**: users, user_thanks, user_statement_endorsements, user_watchlist, watchlist_notifications
- **Statistics**: user_daily_stats, general_daily_stats, backlink_statistics
- **Other**: entity_redirects, entity_backlinks, lexeme_terms

**Documentation**: See `STORAGE-ARCHITECTURE.md` for complete Vitess schema.

### 7. Key Features

#### Content Deduplication
- **Statements**: Deduplicated across all entities
- **References**: Deduplicated across statements
- **Qualifiers**: Deduplicated across statements
- **Snaks**: Deduplicated across statements, qualifiers, references
- **Terms**: Deduplicated across entities (labels, descriptions, aliases)
- **Sitelinks**: Deduplicated across entities

**Storage Savings**: ~90% reduction compared to inline storage.

**Documentation**: See `STATEMENT-DEDUPLICATION.md` for details.

#### Range-Based ID Generation
- Pre-allocates ID ranges for high-throughput creation
- Worker ensures ranges always available
- Atomic ID claims with confirmation
- No coordination required for allocation

**Documentation**: See `ENTITY-MODEL.md` for complete ID generation details.

#### Social Features
- **Thanks**: Thank users for specific revisions
- **Endorsements**: Endorse statements to signal trust
- **Watchlist**: Track entity changes with notifications

**Documentation**: See separate sections in `ARCHITECTURE/` for each feature.

#### RDF Export
- **Formats**: Turtle, RDF XML, NTriples
- **Diffing**: RDF diffs between revisions
- **Streaming**: Real-time RDF change events
- **Canonicalization**: URDNA2015 for consistent blank node handling

**Documentation**: See `RDF-BUILDER/` directory for RDF architecture.

#### Statistics
- **User Stats**: Daily user activity statistics
- **General Stats**: Daily wiki-wide statistics
- **Backlink Stats**: Periodic backlink counts

**Documentation**: See `STATISTICS.md` for statistics architecture.

### 8. Configuration

All settings managed via environment variables:

**Database**: VITESS_HOST, VITESS_PORT, VITESS_DATABASE, VITESS_USER, VITESS_PASSWORD

**Storage**: S3_ENDPOINT, S3_ACCESS_KEY, S3_SECRET_KEY, S3_*_BUCKET

**Streaming**: KAFKA_BROKERS, STREAMING_ENABLED, KAFKA_*_TOPIC

**API**: API_PREFIX, ENTITY_VERSION

**Workers**: *_STATS_ENABLED, *_STATS_SCHEDULE

**Documentation**: See `CONFIGURATION.md` for complete configuration reference.

### 9. Transaction Model

#### Atomicity
- All Vitess operations wrapped in database transactions
- S3 operations tracked for rollback
- Ref counts ensure consistency

#### Isolation
- Read committed isolation level
- No dirty reads, non-repeatable reads prevented

#### Durability
- Vitess: Durable storage (MySQL)
- S3: Durable object storage
- Kafka: Durable event streaming

#### Consistency
- Eventual consistency for stats workers
- Strong consistency for entity CRUD operations
- Ref counting ensures statement consistency

### 10. Performance Characteristics

#### Scalability
- **Horizontal scaling**: S3 and Kafka scale horizontally
- **Vertical scaling**: Vitess can be sharded
- **Throughput**: Supports thousands of operations per second

#### Latency
- **Entity read**: ~200-500ms (including hash content loading)
- **Entity create**: ~300-600ms (including S3 writes)
- **Statement read**: ~50-150ms
- **RDF export**: ~500-1000ms per entity

#### Storage Efficiency
- **Deduplication**: ~90% storage savings
- **Compression**: Optional for S3 objects
- **CDN caching**: Enabled for public buckets

### 11. Security Considerations

#### Authentication
- User authentication via MediaWiki tokens (not implemented yet)
- API keys for external access (not implemented yet)

#### Authorization
- Edit rights via MediaWiki user permissions (not implemented yet)
- Protected entities via `semi_protected`, `locked`, `mass_edit_protected` flags

#### Data Protection
- No sensitive data in logs
- Secure credential management via environment variables
- S3 bucket access control

### 12. Monitoring and Observability

#### Health Checks
- `GET /health` - API health check
- Worker health endpoints
- Database connection monitoring
- S3 connectivity monitoring

#### Logging
- Structured logging with request IDs
- Log levels: DEBUG, INFO, WARNING, ERROR
- Audit logging for entity operations (optional)

#### Metrics
- Request latency histograms
- Error rate tracking
- Storage usage monitoring
- Worker execution timing

## Related Documentation

- [STORAGE-ARCHITECTURE.md](./STORAGE-ARCHITECTURE.md) - S3 and Vitess storage design
- [ENTITY-MODEL.md](./ENTITY-MODEL.md) - Entity ID strategy and models
- [REPOSITORIES.md](./REPOSITORIES.md) - Repository classes for data access
- [WORKERS.md](./WORKERS.md) - Background worker architecture
- [CONFIGURATION.md](./CONFIGURATION.md) - Configuration options
- [API_MODELS.md](./API_MODELS.md) - REST API request/response models
- [SERVICES.md](./SERVICES.md) - Service layer architecture
- [CONCURRENCY-CONTROL.md](./CONCURRENCY-CONTROL.md) - Concurrency control details
- [CONSISTENCY-MODEL.md](./CONSISTENCY-MODEL.md) - Consistency model
- [CACHING-STRATEGY.md](./CACHING-STRATEGY.md) - Caching architecture
- [BULK-OPERATIONS.md](./BULK-OPERATIONS.md) - Bulk operation support
- [SCALING-PROPERTIES.md](./SCALING-PROPERTIES.md) - Scaling characteristics
- [ARCHITECTURE-CHANGELOG.md](./ARCHITECTURE-CHANGELOG.md) - Architectural changes history
- [RDF-BUILDER/RDF-ENDPOINT-ARCHITECTURE.md](RDF-BUILDER/RDF-ENDPOINT-ARCHITECTURE.md) - RDF generation and diffing
- [CHANGE-STREAMING/CHANGE-NOTIFICATION.md](CHANGE-STREAMING/CHANGE-NOTIFICATION.md) - Event streaming architecture
