# Services Overview

This document describes the service layer in Wikibase backend system.

## Overview

The service layer contains business logic and high-level operations that coordinate between REST API handlers, repositories, and infrastructure components.

## Service Architecture

Services are organized by domain and functionality:

### Entity Services
Located in `src/models/rest_api/entitybase/v1/services/`

- **General Stats Service**: Computes general wiki statistics
- **User Stats Service**: Computes user statistics  
- **Redirect Service**: Manages entity redirects

### Entity Handlers
Located in `src/models/rest_api/entitybase/v1/handlers/`

#### Base Handler
- **EntityHandler** (`src/models/rest_api/entitybase/v1/handlers/entity/handler.py`): Base handler with common entity operations

#### CRUD Handlers
- **EntityCreateHandler** (`src/models/rest_api/entitybase/v1/handlers/entity/create.py`): Entity creation logic
- **EntityUpdateHandler** (`src/models/rest_api/entitybase/v1/handlers/entity/update.py`): Entity update logic
- **EntityDeleteHandler** (`src/models/rest_api/entitybase/v1/handlers/entity/delete.py`): Entity deletion logic

#### Specialized Handlers
- **RedirectHandler** (`src/models/rest_api/entitybase/v1/handlers/entity/redirect.py`): Redirect management
- **RevertHandler** (`src/models/rest_api/entitybase/v1/handlers/entity/revert.py`): Revision revert logic
- **PropertyCreateHandler** (`src/models/rest_api/entitybase/v1/handlers/entity/property/create.py`): Property creation
- **LexemeCreateHandler** (`src/models/rest_api/entitybase/v1/handlers/entity/lexeme/create.py`): Lexeme creation

#### Statement Handlers
- **StatementHandler** (`src/models/rest_api/entitybase/v1/handlers/statement.py`): Statement CRUD operations

#### User Features Handlers
- **UserHandler** (`src/models/rest_api/entitybase/v1/handlers/user.py`): User operations
- **ThanksHandler** (`src/models/rest_api/entitybase/v1/handlers/thanks.py`): Thanks feature
- **EndorsementHandler** (`src/models/rest_api/entitybase/v1/handlers/endorsements.py`): Endorsements feature
- **WatchlistHandler** (`src/models/rest_api/entitybase/v1/handlers/watchlist.py`): Watchlist management

### Transaction Classes
- **CreationTransaction** (`src/models/rest_api/entitybase/v1/handlers/entity/creation_transaction.py`): Manages entity creation transaction
- **UpdateTransaction** (`src/models/rest_api/entitybase/v1/handlers/entity/update_transaction.py`): Manages entity update transaction
- **EntityTransaction** (`src/models/rest_api/entitybase/v1/handlers/entity/entity_transaction.py`): Base transaction class

### Infrastructure Services

#### S3 Storage Services
- **StatementStorage** (`src/models/infrastructure/s3/storage/statement_storage.py`): Statement storage operations
- **ReferenceStorage** (`src/models/infrastructure/s3/storage/reference_storage.py`): Reference storage operations
- **QualifierStorage** (`src/models/infrastructure/s3/storage/qualifier_storage.py`): Qualifier storage operations
- **SnakStorage** (`src/models/infrastructure/s3/storage/snak_storage.py`): Snak storage operations
- **LexemeStorage** (`src/models/infrastructure/s3/storage/lexeme_storage.py`): Lexeme forms and senses storage
- **MetadataStorage** (`src/models/infrastructure/s3/storage/metadata_storage.py`): Term and sitelink metadata storage
- **RevisionStorage** (`src/models/infrastructure/s3/storage/revision_storage.py`): Revision storage operations

#### RDF Builder Services
- **EntityConverter** (`src/models/rdf_builder/converter.py`): Convert entities to RDF
- **EntityDiffWorker** (`src/models/workers/entity_diff/entity_diff_worker.py`): Compute RDF diffs
- **RDFSerializer** (`src/models/workers/entity_diff/rdf_serializer.py`): Serialize to RDF formats
- **IncrementalRDFUpdater** (`src/models/rdf_builder/incremental_updater.py`): Apply diffs incrementally

#### ID Generation
- **EnumerationService** (`src/models/infrastructure/vitess/enumeration_service.py`): Range-based ID allocation
- **IdResolver** (`src/models/infrastructure/vitess/id_resolver.py`): Resolve entity IDs

## Common Patterns

### Handler Structure
```python
class EntityHandler:
    def __init__(self, state_handler):
        self.state_handler = state_handler
        self.vitess_client = state_handler.vitess_client
        self.s3_client = state_handler.s3_client
        self.entity_change_stream_producer = state_handler.entity_change_stream_producer
    
    def create_entity(self, request, edit_headers, validator):
        """Create entity with proper transaction handling."""
        pass
```

### Transaction Pattern
```python
class UpdateTransaction(EntityTransaction):
    def __init__(self, entity_id, vitess_client, s3_client):
        super().__init__(entity_id, vitess_client, s3_client)
        self.rollback_operations = []
    
    def process_statements(self, statements):
        """Process and store statements within transaction."""
        pass
    
    def commit(self):
        """Commit all changes."""
        pass
    
    def rollback(self):
        """Rollback all changes (S3 + Vitess)."""
        pass
```

## Related Documentation

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Overall system architecture
- [REPOSITORIES.md](./REPOSITORIES.md) - Repository layer for data access
- [STORAGE-ARCHITECTURE.md](./STORAGE-ARCHITECTURE.md) - S3 and Vitess storage
- [WORKERS.md](./WORKERS.md) - Background workers
