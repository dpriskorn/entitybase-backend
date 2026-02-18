# Entitybase Backend

A clean-room, billion-scale Wikibase JSON and RDF schema compatible backend architecture 
based on immutable S3 snapshots and Vitess indexing.

It is designed to support 1bn+ entities and 1tn unique statements.

## Core Principles

**The Immutable Revision Invariant:**

A revision is an immutable snapshot stored in S3. Once written, it never changes.

- No mutable revisions
- No diff storage
- No page-based state
- No MediaWiki-owned content

Everything else in the system derives from this rule.

## Architecture Overview

### System Architecture

The Entitybase Backend implements a microservices architecture designed for billion-scale Wikibase operations:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Service   │    │   ID Generator  │    │   Dump Worker   │    │   Dev Worker    │
│                 │    │   (Worker)      │    │   (Worker)      │    │   (Development) │
│ • REST API      │    │ • Range-based   │    │ • JSONL Dump    │    │ • Bucket setup  │
│ • CRUD Ops      │    │   ID allocation │    │   Generation    │    │ • Health checks │
│ • Validation    │    │ • Atomic ops    │    │ • Shard export  │    │ • Environment   │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         └───────────────────────┼───────────────────────┼───────────────────────┘
                                 │                       │
                     ┌─────────────────────┐    ┌─────────────────────┐
                     │                     │    │                     │
                     │   Storage Stack     │    │   S3 Buckets        │
                     │                     │    │                     │
                     │ • S3 (immutable     │    │ • terms (metadata)  │
                     │   snapshots)       │    │ • statements (dedup)│
                     │ • Vitess (indexing)│    │ • references        │
                     │ • Event streaming  │    │ • qualifiers        │
                     │                     │    │ • revisions (data)  │
                     │                     │    │ • sitelinks         │
                     │                     │    │ • snaks             │
                     │                     │    │ • wikibase-dumps    │
                     └─────────────────────┘    └─────────────────────┘
```

### Service Components

#### **API Service (Main Application)**
- **FastAPI-based REST API** serving Wikibase-compatible endpoints
- **Type-specific CRUD operations**:
  - `POST /item` - Create items (auto-assign Q IDs)
  - `PUT /item/Q{id}` - Update items
  - `GET /item/Q{id}` - Read items
  - `DELETE /item/Q{id}` - Delete items
  - Similar endpoints for properties (`/property/P{id}`), lexemes (`/lexeme/L{id}`), and entity schemas (`/entityschema/E{id}`)
- **Validation & business logic** for all entity operations
- **Statement deduplication** and RDF generation integration

#### **ID Generator Worker**
- **Range-based ID allocation** to prevent database write hotspots
- **Scalable to 777K+ entities/day** (10 edits/sec, 90% new entities)
- **Atomic operations** via Vitess optimistic locking
- **Auto-scaling** via Docker Compose replicas
- **Health monitoring** and range utilization tracking

#### **Dump Worker Service**
- **JSONL Entity Dumps**: Generate complete entity exports in JSON Lines format
- **S3 Integration**: Store dumps in dedicated S3 bucket
- **Raw Revision Data**: Export full revision content without manipulation
- **Shard-based Processing** (Planned): Process entities by Vitess shard for scalability
- **Parallel Processing** (Planned): Large-scale dump generation

### Storage Stack

#### **S3 (System of Record)**
- **Immutable snapshots**: All entity content stored as immutable S3 objects
- **Versioned storage**: Complete revision history with perfect auditability
- **RDF exports**: Generated TTL files for semantic web consumption
- **Statement deduplication**: Shared statement objects to reduce storage

#### **Vitess (Indexing Layer)**
- **Entity metadata**: Head pointers, timestamps, protection status
- **Statement indexing**: Deduplicated statement references with ref_counts
- **ID range management**: Atomic allocation of entity ID ranges
- **Redirect tracking**: Bidirectional redirect relationships

#### **Event Streaming**
- **Change notifications**: Real-time entity change events
- **RDF streaming**: Continuous RDF triple updates
- **Consumer decoupling**: Asynchronous processing of entity changes

### Key Concepts

- **Entity**: A logical identifier (Q123, P456, etc.) with no intrinsic state
- **Revision**: Complete, immutable S3 snapshot of entity state
- **Head Pointer**: Current revision managed via compare-and-swap in Vitess
- **Statement Deduplication**: Shared statement objects with reference counting
- **ID Ranges**: Pre-allocated blocks of entity IDs to prevent write hotspots

### Scaling Characteristics

- **Entity Creation**: 777K/day sustained (10 edits/sec, 90% new entities)
- **Storage Growth**: 2.84B entities over 10 years
- **Read Performance**: Sub-millisecond via S3 + Vitess caching
- **Write Performance**: Range-based ID allocation eliminates bottlenecks

### Service Components

#### **Dev Worker Service** ✅
- **Bucket Management**: Automated MinIO bucket creation and health checks
- **Environment Setup**: Development infrastructure provisioning
- **CLI Interface**: Command-line tools for bucket operations
- **Health Monitoring**: Bucket accessibility and status reporting

**Key Features**:
- Eight specialized buckets (terms, statements, references, qualifiers, revisions, sitelinks, snaks, wikibase-dumps)
- Idempotent setup operations
- Development workflow integration
- Incremental change streaming for real-time RDF updates
- Compression and partitioning for efficient storage/distribution
- Health monitoring and progress tracking
- Integration with existing RDF builder infrastructure

#### **Additional Services (Future)**
- **Validation Worker**: Background validation of entity data
- **Analytics Service**: Usage statistics and performance monitoring
- **Replication Service**: Cross-region data replication
- **Backup Service**: Automated S3/Vitess backup coordination

## Getting Started

Start with [ARCHITECTURE.md](./doc/ARCHITECTURE/ARCHITECTURE.md) for the complete architecture overview.

### Quick Start

```bash
# Start the full stack
docker-compose up -d

# API available at http://localhost:8000
# MinIO console at http://localhost:9001
# Vitess admin at http://localhost:15100
```

#### MinIO Bucket Setup

The system uses eight S3-compatible buckets for different data types:

- **`terms`**: Stores entity metadata (labels, descriptions, aliases)
- **`statements`**: Stores statement content with deduplication
- **`references`**: Stores reference data
- **`qualifiers`**: Stores qualifier data
- **`revisions`**: Stores revision data and metadata
- **`sitelinks`**: Stores sitelink data
- **`snaks`**: Stores snak data
- **`wikibase-dumps`**: Stores entity export dumps

Use either the setup script or dev worker CLI to create these buckets automatically.

### Design Philosophy

- **Immutability**: All content is stored as immutable snapshots
- **Eventual consistency**: With reconciliation guarantees and no data loss
- **Horizontal scalability**: S3 for storage, Vitess for indexing, workers for specialized tasks
- **Microservices architecture**: Dedicated services for API, ID generation, and dump processing
- **Auditability**: Perfect revision history by design
- **Decoupling**: MediaWiki + Wikibase becomes a stateless API client
- **Performance-first**: Range-based ID allocation eliminates write hotspots
- **Type safety**: Dedicated endpoints for each Wikibase entity type

## Features

### Redirect Support
- **Create redirects**: Entity API endpoint to mark entities as redirects to other entities
- **Revert redirects**: Entity API endpoint to revert redirects back to normal entities using revision-based restore
- **RDF generation**: RDF builder generates `owl:sameAs` statements for all incoming redirects
- **Vitess integration**: Redirects stored in Vitess `entity_redirects` table for efficient querying
- **S3 schema v1.1.0**: Added `redirects_to` field to mark redirect entities
- **Immutable tombstones**: Redirect entities have empty entity data with only `redirects_to` field
- **Authoritative source**: Vitess is the single source of truth for redirect relationships
- **Test cache fallback**: File-based cache for testing without Vitess connection

### Statement Deduplication
- **Hash-based storage**: All statements stored as deduplicated objects with hash-based references
- **Property-based loading**: Efficient fetching of statements by property with counts for intelligent loading
- **Most-used analytics**: Query most used statements across the system for scientific analysis
- **Orphaned cleanup**: Background job for cleaning up orphaned statements (ref_count=0)

### Entity Protection
- **Lock/Unlock**: `/entities/{entity_id}/lock` (POST/DELETE) - Full edit lock
- **Archive/Unarchive**: `/entities/{entity_id}/archive` (POST/DELETE) - Archive entities
- **Semi-protect/Unprotect**: `/entities/{entity_id}/semi-protect` (POST/DELETE) - Semi-protection
- **Mass-edit-protect/Unprotect**: `/entities/{entity_id}/mass-edit-protect` (POST/DELETE) - Mass edit protection
- **Idempotent**: All protection endpoints return success if entity is already in target state

### Type-Specific Endpoints
- **Item endpoints**: `/item` for item entities (Q IDs)
- **Property endpoints**: `/property` for property entities (P IDs)
- **Lexeme endpoints**: `/lexeme` for lexeme entities (L IDs)

# License
GPLv3+ 

# Copyright 
Nizo Priskorn 2026 

## External links
* https://www.mediawiki.org/wiki/User:So9q/Scaling_issues Implemenatation history and on-wiki details
