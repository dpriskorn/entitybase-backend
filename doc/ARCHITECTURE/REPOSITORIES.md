# Repository Classes Overview

This document provides a quick reference to all repository classes that handle data access in the Wikibase backend.

## Vitess Repositories

### Core Entity Repositories

- **EntityRepository** - `src/models/infrastructure/vitess/repositories/entity.py` - Entity metadata operations and ID resolution

- **HeadRepository** - `src/models/infrastructure/vitess/repositories/head.py` - Head revision tracking and current entity state

- **RevisionRepository** - `src/models/infrastructure/vitess/repositories/revision.py` - Revision metadata and history

### Statement and Content Repositories

- **StatementRepository** - `src/models/infrastructure/vitess/repositories/statement.py` - Statement content tracking and deduplication

- **BacklinkRepository** - `src/models/infrastructure/vitess/repositories/backlink.py` - Backlink tracking and management

- **RedirectRepository** - `src/models/infrastructure/vitess/repositories/redirect.py` - Entity redirect management

### User Feature Repositories

- **UserRepository** - `src/models/infrastructure/vitess/repositories/user.py` - User data and preferences

- **WatchlistRepository** - `src/models/infrastructure/vitess/repositories/watchlist.py` - Watchlist management and notifications

- **EndorsementRepository** - `src/models/infrastructure/vitess/repositories/endorsement.py` - Statement endorsements

- **ThanksRepository** - `src/models/infrastructure/vitess/repositories/thanks.py` - Thanks between users

### Metadata and Terms Repositories

- **MetadataRepository** - `src/models/infrastructure/vitess/repositories/metadata.py` - Entity metadata (labels, descriptions, aliases)

- **TermsRepository** - `src/models/infrastructure/vitess/repositories/terms.py` - Term management with deduplication

- **LexemeRepository** - `src/models/infrastructure/vitess/repositories/lexeme_repository.py` - Lexeme forms and senses

### Statistics Repositories

- **ListingRepository** - `src/models/infrastructure/vitess/repositories/listing.py` - Entity listings and pagination

- **SchemaRepository** - `src/models/infrastructure/vitess/repositories/schema.py` - Database schema creation and management

### Base Repository

- **Repository** - `src/models/infrastructure/vitess/repository.py` - Base repository class with common functionality

---

## S3 Storage Repositories

### Revision Storage

- **RevisionStorage** - `src/models/infrastructure/s3/storage/revision_storage.py` - Revision snapshot storage and retrieval

### Content Storage

- **StatementStorage** - `src/models/infrastructure/s3/storage/statement_storage.py` - Statement content storage

- **ReferenceStorage** - `src/models/infrastructure/s3/storage/reference_storage.py` - Reference storage

- **QualifierStorage** - `src/models/infrastructure/s3/storage/qualifier_storage.py` - Qualifier storage

- **SnakStorage** - `src/models/infrastructure/s3/storage/snak_storage.py` - Snak storage

- **MetadataStorage** - `src/models/infrastructure/s3/storage/metadata_storage.py` - Term and sitelink metadata storage

### Specialized Storage

- **LexemeStorage** - `src/models/infrastructure/s3/storage/lexeme_storage.py` - Lexeme forms and senses storage

### Base Storage

- **BaseStorage** - `src/models/infrastructure/s3/base_storage.py` - Base S3 storage class

---

## Stream Repositories

### Kafka Producers

- **EntityChangeStreamProducer** - Kafka producer for entity change events (entitybase.entity_change topic)

- **EntityDiffStreamProducer** - Kafka producer for entity diff events (wikibase.entity_diff topic)

### Kafka Consumers

- **Consumer** - `src/models/infrastructure/stream/consumer.py` - Generic Kafka consumer for event processing

---

## Infrastructure Components

### Connections

- **VitessClient** - `src/models/infrastructure/vitess/client.py` - Vitess database client and connection management

- **VitessConnection** - `src/models/infrastructure/vitess/connection.py` - Vitess connection handler

- **S3Client** - `src/models/infrastructure/s3/client.py` - S3 client and connection management

- **S3Connection** - `src/models/infrastructure/s3/connection.py` - S3 connection handler

### Utilities

- **IdResolver** - `src/models/infrastructure/vitess/id_resolver.py` - Resolve entity IDs between external and internal IDs

- **UniqueIdGenerator** - `src/models/infrastructure/unique_id.py` - Unique ID generation for various purposes

- **EnumerationService** - Range-based ID allocation service (Q, P, L, E IDs)

---

## Architecture Notes

### Connection Management
- All repositories receive a `connection_manager` for database access
- Connections are managed through VitessClient and S3Client
- Connection pooling is handled at the client level

### Transaction Safety
- Methods should be called within connection contexts
- Vitess operations use database transactions for ACID guarantees
- S3 operations are tracked for rollback capability

### Error Handling
- Repositories raise exceptions for database errors
- S3 operations raise S3-specific exceptions
- HTTP and connection errors are propagated up the stack

### Performance
- Methods are optimized for common query patterns
- Indexes are defined in schema for frequently accessed columns
- Reference counting enables efficient content deduplication

### Data Integrity
- Foreign key relationships are maintained at the application level
- Orphaned content can be identified via `ref_count = 0`
- ID ranges ensure no duplicate entity IDs

---

## Related Documentation

- [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md) - Complete database schema reference
- [STORAGE-ARCHITECTURE.md](./STORAGE-ARCHITECTURE.md) - S3 and Vitess storage design
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Overall system architecture
- [ENTITY-MODEL.md](./ENTITY-MODEL.md) - Entity ID strategy and models
