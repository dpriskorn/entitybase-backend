# Architecture Diagrams

Visual diagrams showing how the Entitybase system works.

## System Overview

- [System Architecture](png/system_architecture.png) - High-level system design
- [Data Flow](png/data_flow.png) - How data moves through the system
- [Detailed Data Flow](png/detailed_data_flow.png) - Full data flow with deduplication

## Components

- [API Components](png/detailed_api_components.png) - REST API architecture
- [Service Components](png/detailed_service_components.png) - Business logic layer
- [Worker Components](png/detailed_worker_components.png) - Background workers
- [Infrastructure](png/detailed_infrastructure_components.png) - S3, Vitess, streaming
- [Data Models](png/detailed_model_components.png) - Internal representation
- [Component Relationships](png/component_relationships.png) - How components interact

## Read Paths

- [Entity Get Process](READ-PATHS/ENTITIES-GET-PROCESS.md) - How entity reads work

## Write Paths

- [Entity Create](WRITE-PATHS/ENTITY-CREATE-PROCESS.md) - Creating new entities
- [Entity Update](WRITE-PATHS/ENTITY-UPDATE-PROCESS.md) - Updating entities
- [Terms PUT](WRITE-PATHS/TERMS-PUT.md) - Setting terms
- [Terms PATCH](WRITE-PATHS/TERMS-PATCH.md) - Updating terms
- [Terms DELETE](WRITE-PATHS/TERMS-DELETE.md) - Deleting terms
- [Delete/Undelete](WRITE-PATHS/DELETE-UNDELETE-PROCESS.md) - Entity deletion
- [Archive/Unarchive](WRITE-PATHS/ARCHIVE-UNARCHIVE-PROCESS.md) - Archiving entities
- [Lock/Unlock](WRITE-PATHS/LOCK-UNLOCK-PROCESS.md) - Entity protection
- [Redirect](WRITE-PATHS/REDIRECT-WRITE-PROCESS.md) - Entity redirects
- [Statement Processing](WRITE-PATHS/STATEMENT-PROCESSING-PATHS.md) - Statement handling
- [Lexeme Update](WRITE-PATHS/LEXEME-UPDATE-PROCESS.md) - Lexeme-specific updates
