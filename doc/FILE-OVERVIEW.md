# Documentation Tree

Comprehensive guide to all documentation in the Wikibase Backend project.

## Quick Start

- **[README.md](../../README.md)** - Project overview and quick start
- **[AGENTS.md](../../AGENTS.md)** - Instructions for AI agents working on this codebase
- **[DEVELOPMENT.md](../../DEVELOPMENT.md)** - Development setup and workflow

## Architecture Documentation

### Core Architecture

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Overall system architecture, components, and data flow
- **[STORAGE-ARCHITECTURE.md](./STORAGE-ARCHITECTURE.md)** - S3 and Vitess storage design, schemas, and operations
- **[ENTITY-MODEL.md](./ENTITY-MODEL.md)** - Entity ID strategy and range-based generation
- **[CONCEPTUAL-MODEL.md](./CONCEPTUAL-MODEL.md)** - High-level conceptual model of Wikibase entities

### Components

- **[WORKERS.md](./WORKERS.md)** - Background worker architecture and implementation
- **[REPOSITORIES.md](./REPOSITORIES.md)** - Repository classes for Vitess and S3 data access
- **[API_MODELS.md](./API_MODELS.md)** - REST API request and response models
- **[SERVICES.md](./SERVICES.md)** - Service layer architecture and business logic
- **[CONFIGURATION.md](./CONFIGURATION.md)** - Configuration options and environment variables
- **[DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md)** - Complete database schema reference

### Architecture Patterns

- **[CONCURRENCY-CONTROL.md](./CONCURRENCY-CONTROL.md)** - Concurrency control mechanisms
- **[CONSISTENCY-MODEL.md](./CONSISTENCY-MODEL.md)** - Consistency guarantees and failure recovery
- **[CACHING-STRATEGY.md](./CACHING-STRATEGY.md)** - Caching architecture and cost control
- **[BULK-OPERATIONS.md](./BULK-OPERATIONS.md)** - Bulk operation support and patterns
- **[SCALING-PROPERTIES.md](./SCALING-PROPERTIES.md)** - Scaling characteristics and limits

### Storage Architecture

- **[S3-STORAGE.md](./S3-STORAGE.md)** - S3 storage design and operations
- **[S3/S3-REVISION-ID-STRATEGY.md](./S3/S3-REVISION-ID-STRATEGY.md)** - Revision ID strategy
- **[S3/S3-REVISION-SCHEMA-EVOLUTION.md](./S3/S3-REVISION-SCHEMA-EVOLUTION.md)** - Schema evolution and migration
- **[S3/S3-REVISION-SCHEMA-CHANGELOG.md](./S3/S3-REVISION-SCHEMA-CHANGELOG.md)** - Schema version history
- **[S3/S3-ENTITY-DELETION.md](./S3/S3-ENTITY-DELETION.md)** - Entity deletion strategy

### RDF and Semantics

- **[RDF-BUILDER/RDF-ARCHITECTURE.md](./RDF-BUILDER/RDF-ARCHITECTURE.md)** - RDF generation architecture
- **[RDF-BUILDER/RDF-BUILDER-IMPLEMENTATION.md](./RDF-BUILDER/RDF-BUILDER-IMPLEMENTATION.md)** - RDF builder implementation
- **[RDF-BUILDER/JSON-RDF-CONVERTER.md](./RDF-BUILDER/JSON-RDF-CONVERTER.md)** - JSON to RDF conversion
- **[RDF-BUILDER/RDF-DIFF-STRATEGY.md](./RDF-BUILDER/RDF-DIFF-STRATEGY.md)** - RDF diff computation
- **[RDF-BUILDER/RDF-ENDPOINT-ARCHITECTURE.md](./RDF-BUILDER/RDF-ENDPOINT-ARCHITECTURE.md)** - RDF endpoint design
- **[RDF-BUILDER/RDF-IMPLEMENTATION-STATUS.md](./RDF-BUILDER/RDF-IMPLEMENTATION-STATUS.md)** - RDF feature implementation status

### Change Streaming

- **[CHANGE-STREAMING/CHANGE-NOTIFICATION.md](./CHANGE-STREAMING/CHANGE-NOTIFICATION.md)** - Change notification and event streaming
- **[CHANGE-STREAMING/REST-API-STREAMING-INTEGRATION.md](./CHANGE-STREAMING/REST-API-STREAMING-INTEGRATION.md)** - API and streaming integration
- **[CHANGE-STREAMING/CHANGE-DETECTION-RDF-GENERATION.md](./CHANGE-STREAMING/CHANGE-DETECTION-RDF-GENERATION.md)** - Change detection and RDF generation
- **[CHANGE-STREAMING/CONTINUOUS-RDF-CHANGE-STREAMER.md](./CHANGE-STREAMING/CONTINUOUS-RDF-CHANGE-STREAMER.md)** - Continuous RDF change streaming

### Parser and Internal Representation

- **[PARSER/INTERNAL-REPRESENTATION.md](./PARSER/INTERNAL-REPRESENTATION.md)** - Internal entity representation model
- **[STATEMENT-DEDUPLICATION.md](./STATEMENT-DEDUPLICATION.md)** - Statement deduplication architecture

### Other Architecture

- **[FRONTEND-INTEGRATION-GUIDE.md](./FRONTEND-INTEGRATION-GUIDE.md)** - Frontend integration guide
- **[MEDIAWIKI-INDEPENDENT-CHANGE-DETECTION.md](./MEDIAWIKI-INDEPENDENT-CHANGE-DETECTION.md)** - MediaWiki-independent change detection
- **[WEEKLY-RDF-DUMP-GENERATOR.md](./WEEKLY-RDF-DUMP-GENERATOR.md)** - Weekly RDF dump generation

## Diagrams

- **[DIAGRAMS/README.md](../DIAGRAMS/README.md)** - Architecture diagrams (PlantUML)
- **[DIAGRAMS/system_architecture.puml](../DIAGRAMS/system_architecture.puml)** - System architecture diagram
- **[DIAGRAMS/data_flow.puml](../DIAGRAMS/data_flow.puml)** - Data flow diagram
- **[DIAGRAMS/component_relationships.puml](../DIAGRAMS/component_relationships.puml)** - Component relationships
- **[DIAGRAMS/detailed_api_components.puml](../DIAGRAMS/detailed_api_components.puml)** - API components
- **[DIAGRAMS/detailed_model_components.puml](../DIAGRAMS/detailed_model_components.puml)** - Model components
- **[DIAGRAMS/detailed_service_components.puml](../DIAGRAMS/detailed_service_components.puml)** - Service components
- **[DIAGRAMS/detailed_worker_components.puml](../DIAGRAMS/detailed_worker_components.puml)** - Worker components
- **[DIAGRAMS/detailed_infrastructure_components.puml](../DIAGRAMS/detailed_infrastructure_components.puml)** - Infrastructure components

### Write Path Diagrams

- **[DIAGRAMS/WRITE-PATHS/ENTITY-CREATE-PROCESS.md](../DIAGRAMS/WRITE-PATHS/ENTITY-CREATE-PROCESS.md)** - Entity creation process
- **[DIAGRAMS/WRITE-PATHS/ENTITY-UPDATE-PROCESS.md](../DIAGRAMS/WRITE-PATHS/ENTITY-UPDATE-PROCESS.md)** - Entity update process
- **[DIAGRAMS/WRITE-PATHS/LEXEME-UPDATE-PROCESS.md](../DIAGRAMS/WRITE-PATHS/LEXEME-UPDATE-PROCESS.md)** - Lexeme update process
- **[DIAGRAMS/WRITE-PATHS/STATEMENT-PROCESSING-PATHS.md](../DIAGRAMS/WRITE-PATHS/STATEMENT-PROCESSING-PATHS.md)** - Statement processing
- **[DIAGRAMS/WRITE-PATHS/TERMS-PATCH.md](../DIAGRAMS/WRITE-PATHS/TERMS-PATCH.md)** - Terms patch operation
- **[DIAGRAMS/WRITE-PATHS/TERMS-PUT.md](../DIAGRAMS/WRITE-PATHS/TERMS-PUT.md)** - Terms PUT operation
- **[DIAGRAMS/WRITE-PATHS/TERMS-DELETE.md](../DIAGRAMS/WRITE-PATHS/TERMS-DELETE.md)** - Terms DELETE operation
- **[DIAGRAMS/WRITE-PATHS/DELETE-UNDELETE-PROCESS.md](../DIAGRAMS/WRITE-PATHS/DELETE-UNDELETE-PROCESS.md)** - Delete/undelete process
- **[DIAGRAMS/WRITE-PATHS/ARCHIVE-UNARCHIVE-PROCESS.md](../DIAGRAMS/WRITE-PATHS/ARCHIVE-UNARCHIVE-PROCESS.md)** - Archive/unarchive process
- **[DIAGRAMS/WRITE-PATHS/LOCK-UNLOCK-PROCESS.md](../DIAGRAMS/WRITE-PATHS/LOCK-UNLOCK-PROCESS.md)** - Lock/unlock process
- **[DIAGRAMS/WRITE-PATHS/REDIRECT-WRITE-PROCESS.md](../DIAGRAMS/WRITE-PATHS/REDIRECT-WRITE-PROCESS.md)** - Redirect write process

### Read Path Diagrams

- **[DIAGRAMS/READ-PATHS/ENTITIES-GET-PROCESS.md](../DIAGRAMS/READ-PATHS/ENTITIES-GET-PROCESS.md)** - Entity GET process

## Wikidata Integration

- **[WIKIDATA/README.md](../WIKIDATA/README.md)** - Wikidata integration overview
- **[WIKIDATA/RDF-DATA-MODEL.md](../WIKIDATA/RDF-DATA-MODEL.md)** - Wikidata RDF data model
- **[WIKIDATA/DATATYPES.md](../WIKIDATA/DATATYPES.md)** - Wikidata datatypes
- **[WIKIDATA/RDF-PROPERTIES.md](../WIKIDATA/RDF-PROPERTIES.md)** - Wikidata RDF properties
- **[WIKIDATA/PREFIXES.md](../WIKIDATA/PREFIXES.md)** - Wikidata URI prefixes
- **[WIKIDATA/PREFIX-EXAMPLES.md](../WIKIDATA/PREFIX-EXAMPLES.md)** - Prefix usage examples
- **[WIKIDATA/MIGRATION-STRATEGY.md](../WIKIDATA/MIGRATION-STRATEGY.md)** - Migration strategy from Wikidata
- **[WIKIDATA/WIKIPROJECT-DECENTRALIZED-GOVERNANCE.md](../WIKIDATA/WIKIPROJECT-DECENTRALIZED-GOVERNANCE.md)** - Wikidata governance

### Wikidata Existing Components

- **[WIKIDATA/EXISTING-COMPONENTS/EVENTGATE.md](../WIKIDATA/EXISTING-COMPONENTS/EVENTGATE.md)** - EventGate service
- **[WIKIDATA/EXISTING-COMPONENTS/EVENTSTREAMS.md](../WIKIDATA/EXISTING-COMPONENTS/EVENTSTREAMS.md)** - EventStreams service
- **[WIKIDATA/EXISTING-COMPONENTS/EVENTBUS.md](../WIKIDATA/EXISTING-COMPONENTS/EVENTBUS.md)** - EventBus service
- **[WIKIDATA/EXISTING-COMPONENTS/KAFKASSE.md](../WIKIDATA/EXISTING-COMPONENTS/KAFKASSE.md)** - Kafka SSE
- **[WIKIDATA/EXISTING-COMPONENTS/WIKIDATA-QUERY-RDF.md](../WIKIDATA/EXISTING-COMPONENTS/WIKIDATA-QUERY-RDF.md)** - Query Service
- **[WIKIDATA/EXISTING-COMPONENTS/STREAMING-UPDATER-PRODUCER.md](../WIKIDATA/EXISTING-COMPONENTS/STREAMING-UPDATER-PRODUCER.md)** - Streaming updater producer
- **[WIKIDATA/EXISTING-COMPONENTS/STREAMING-UPDATER-CONSUMER.md](../WIKIDATA/EXISTING-COMPONENTS/STREAMING-UPDATER-CONSUMER.md)** - Streaming updater consumer
- **[WIKIDATA/EXISTING-COMPONENTS/EVENT-PLATFORM-SCHEMA-GUIDELINES.md](../WIKIDATA/EXISTING-COMPONENTS/EVENT-PLATFORM-SCHEMA-GUIDELINES.md)** - Event platform schemas
- **[WIKIDATA/EXISTING-COMPONENTS/SCHEMAS-EVENT-PRIMARY-SUMMARY.md](../WIKIDATA/EXISTING-COMPONENTS/SCHEMAS-EVENT-PRIMARY-SUMMARY.md)** - Event schemas

### Wikidata Operations

- **[WIKIDATA/REVISION-CREATE.md](../WIKIDATA/REVISION-CREATE.md)** - Revision creation
- **[WIKIDATA/RECENTCHANGE.md](../WIKIDATA/RECENTCHANGE.md)** - RecentChange event format
- **[WIKIDATA/KUBERNETES-REQUIREMENTS.md](../WIKIDATA/KUBERNETES-REQUIREMENTS.md)** - Kubernetes deployment

## Optimizations

- **[OPTIMIZATIONS/PACKING.md](../OPTIMIZATIONS/PACKING.md)** - Data packing optimization
- **[OPTIMIZATIONS/COMPRESSION.md](../OPTIMIZATIONS/COMPRESSION.md)** - Compression strategies

## Economic Estimations

- **[ECONOMIC-ESTIMATIONS/VITESS-COST-ESTIMATION.md](../ECONOMIC-ESTIMATIONS/VITESS-COST-ESTIMATION.md)** - Vitess cost estimation
- **[ECONOMIC-ESTIMATIONS/WEEKLY-DUMP-COST-ESTIMATION.md](../ECONOMIC-ESTIMATIONS/WEEKLY-DUMP-COST-ESTIMATION.md)** - Weekly dump cost
- **[ECONOMIC-ESTIMATIONS/STORAGE-COST-ESTIMATIONS.md](../ECONOMIC-ESTIMATIONS/STORAGE-COST-ESTIMATIONS.md)** - Storage cost estimates

## Risk Analysis

- **[RISK/HASH-COLLISION.md](../RISK/HASH-COLLISION.md)** - Hash collision risk analysis

## Experiments

- **[EXPERIMENTS/DOCKER/IMPORT-OF-ALL-PROPERTIES.md](../EXPERIMENTS/DOCKER/IMPORT-OF-ALL-PROPERTIES.md)** - Property import experiment

## Deprecated Documentation

- **[DEPRECATED/README.md](./DEPRECATED/README.md)** - Deprecated documentation index
- **[DEPRECATED/POST-PROCESSING-VALIDATION.md](./DEPRECATED/POST-PROCESSING-VALIDATION.md)** - Post-processing validation (deprecated)
- **[DEPRECATED/JSON-VALIDATION-STRATEGY.md](./DEPRECATED/JSON-VALIDATION-STRATEGY.md)** - JSON validation strategy (deprecated)
- **[DEPRECATED/DATA-FLOW.puml](./DEPRECATED/DATA-FLOW.puml)** - Old data flow diagram (deprecated)

## Source Code Documentation

### Core Models

- **[src/models/data/README.md](../../src/models/data/README.md)** - Data models overview
- **[src/models/rest_api/ENDPOINTS.md](../../src/models/rest_api/ENDPOINTS.md)** - REST API endpoint reference
- **[src/models/rest_api/VERSIONING.md](../../src/models/rest_api/VERSIONING.md)** - API versioning strategy
- **[src/models/rest_api/UNSUPPORTED.md](../../src/models/rest_api/UNSUPPORTED.md)** - Unsupported features

### Internal Components

- **[src/models/json_parser/README.md](../../src/models/json_parser/README.md)** - JSON parser architecture
- **[src/models/rdf_builder/README.md](../../src/models/rdf_builder/README.md)** - RDF builder overview
- **[src/models/rdf_builder/RDF-ARCHITECTURE.md](../../src/models/rdf_builder/RDF-ARCHITECTURE.md)** - RDF architecture details
- **[src/models/rdf_builder/RDF-IMPLEMENTATION-STATUS.md](../../src/models/rdf_builder/RDF-IMPLEMENTATION-STATUS.md)** - RDF implementation status

### RDF Builder Components

- **[src/models/rdf_builder/ontology/README.md](../../src/models/rdf_builder/ontology/README.md)** - Wikibase ontology
- **[src/models/rdf_builder/property_registry/README.md](../../src/models/rdf_builder/property_registry/README.md)** - Property registry
- **[src/models/rdf_builder/hashing/HASHDEDUPEBAG-README.md](../../src/models/rdf_builder/hashing/HASHDEDUPEBAG-README.md)** - Hash deduplication
- **[src/models/rdf_builder/hashing/HASHDEDUPEBAG-IMPLEMENTATION.md](../../src/models/rdf_builder/hashing/HASHDEDUPEBAG-IMPLEMENTATION.md)** - Hash deduplication implementation

## Schemas

- **[schemas/entitybase/entity/2.0.0/README.md](../../schemas/entitybase/entity/2.0.0/README.md)** - Entity schema 2.0.0
- **[schemas/entitybase/entity/1.0.0/README.md](../../schemas/entitybase/entity/1.0.0/README.md)** - Entity schema 1.0.0 (deprecated)
- **[schemas/entitybase/s3/revision/3.0.0/README.md](../../schemas/entitybase/s3/revision/3.0.0/README.md)** - S3 revision schema 3.0.0 (deprecated)
- **[schemas/entitybase/s3/statement/1.0.0/README.md](../../schemas/entitybase/s3/statement/1.0.0/README.md)** - Statement schema 1.0.0
- **[schemas/entitybase/s3/reference/1.0.0/README.md](../../schemas/entitybase/s3/reference/1.0.0/README.md)** - Reference schema 1.0.0
- **[schemas/entitybase/s3/qualifier/1.0.0/README.md](../../schemas/entitybase/s3/qualifier/1.0.0/README.md)** - Qualifier schema 1.0.0
- **[schemas/entitybase/events/entity_change/README.md](../../schemas/entitybase/events/entity_change/README.md)** - Entity change events
- **[schemas/entitybase/events/entity_change/1.0.0/README.md](../../schemas/entitybase/events/entity_change/1.0.0/README.md)** - Entity change event 1.0.0
- **[schemas/entitybase/events/new_thank/1.0.0/README.md](../../schemas/entitybase/events/new_thank/1.0.0/README.md)** - Thank event 1.0.0
- **[schemas/entitybase/events/endorse_change/1.0.0/README.md](../../schemas/entitybase/events/endorse_change/1.0.0/README.md)** - Endorse change event 1.0.0
- **[schemas/entitybase/events/entity_diff/2.0.0/SOURCE.md](../../schemas/entitybase/events/entity_diff/2.0.0/SOURCE.md)** - Entity diff event 2.0.0
- **[schemas/entitybase/entities/1.0.0/README.md](../../schemas/entitybase/entities/1.0.0/README.md)** - Entities event 1.0.0

## Test Data

- **[test_data/README.md](../../test_data/README.md)** - Test data documentation

## Development Tools

### Linters

- **[doc/linters/json-dumps-allowlist.md](../linters/json-dumps-allowlist.md)** - JSON dumps allowlist for linting
- **[run-linters.sh](../../run-linters.sh)** - Run all linters
- **[run-ruff.sh](../../run-ruff.sh)** - Run Ruff linter
- **[run-mypy.sh](../../run-mypy.sh)** - Run MyPy type checker
- **[run-radon.sh](../../run-radon.sh)** - Run Radon complexity analyzer
- **[run-vulture.sh](../../run-vulture.sh)** - Run Vulture dead code detector

### Custom Linters

- **[run-str-lint.sh](../../run-str-lint.sh)** - String linting
- **[run-int-lint.sh](../../run-int-lint.sh)** - Integer linting
- **[run-response-model-lint.sh](../../run-response-model-lint.sh)** - Response model linting
- **[run-logger-lint.sh](../../run-logger-lint.sh)** - Logger linting
- **[run-pydantic-field-lint.sh](../../run-pydantic-field-lint.sh)** - Pydantic field linting
- **[run-tuple-lint.sh](../../run-tuple-lint.sh)** - Tuple linting
- **[run-init-lint.sh](../../run-init-lint.sh)** - __init__ linting
- **[run-any-lint.sh](../../run-any-lint.sh)** - Any linting
- **[run-cast-lint.sh](../../run-cast-lint.sh)** - Cast linting
- **[run-key-length-lint.sh](../../run-key-length-lint.sh)** - Key length linting
- **[run-backslash-lint.sh](../../run-backslash-lint.sh)** - Backslash linting
- **[run-json-lint.sh](../../run-json-lint.sh)** - JSON linting

### Tests

- **[run-unit-tests.sh](../../run-unit-tests.sh)** - Run unit tests
- **[run-coverage.sh](../../run-coverage.sh)** - Run tests with coverage
- **[tests/AGENTS.md](../../tests/AGENTS.md)** - Test instructions for AI agents

## Project Documentation

- **[STATISTICS.md](../../STATISTICS.md)** - Project statistics
- **[TODO.md](../../TODO.md)** - TODO list
- **[LICENSE-DETAILS.md](../LICENSE-DETAILS.md)** - License details
- **[INSTRUCTIONS.md](../../instructions.md)** - General instructions
- **[OPENCODE-INSTRUCTIONS.md](../../OPENCODE-INSTRUCTIONS.md)** - OpenCode agent instructions

## External Integration

- **[external/wikidata-rest-api/README.md](../../external/wikidata-rest-api/README.md)** - Wikidata REST API integration

## Source Code Structure

- **[src/TREE.md](../../src/TREE.md)** - Source code tree structure

## Pydantic Analysis

- **[doc/pydantic/json_dump/README.md](../pydantic/json_dump/README.md)** - model_dump vs json.dumps analysis
- **[doc/pydantic/json_dump/test_len.py](../pydantic/json_dump/test_len.py)** - Test script for JSON length

## Docker

- **[docker/docker-compose.md](../../docker/docker-compose.md)** - Docker Compose configuration
