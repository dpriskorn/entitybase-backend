# Wikibase Backend

A clean-room, billion-scale Wikibase backend architecture based on immutable S3 snapshots and Vitess indexing.

## Overview

This repository defines the architecture for a next-generation Wikibase backend designed for horizontal scalability, perfect audit trails, and clean separation of concerns. It serves as the foundation for building a high-performance, distributed knowledge base system.

## Core Principles

**The Immutable Revision Invariant:**

A revision is an immutable snapshot stored in S3. Once written, it never changes.

- No mutable revisions
- No diff storage
- No page-based state
- No MediaWiki-owned content

Everything else in the system derives from this rule.

## Architecture

### Storage Stack

- **S3**: System of record storing all entity content as immutable snapshots
- **Vitess**: Index and metadata layer storing pointers to S3 objects

### Key Concepts

- **Entity**: A logical identifier (e.g., Q123) with no intrinsic state outside revisions
- **Revision**: Complete, immutable snapshot of an entity
- **Head Pointer**: Current revision pointer managed via compare-and-swap

## Documentation

The architecture is documented across multiple focused documents:

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](./ARCHITECTURE/ARCHITECTURE.md) | Main architecture overview |
| [CONCEPTUAL-MODEL.md](./ARCHITECTURE/CONCEPTUAL-MODEL.md) | Entity and revision concepts |
| [STORAGE-ARCHITECTURE.md](./ARCHITECTURE/STORAGE-ARCHITECTURE.md) | S3 and Vitess storage design |
| [CONSISTENCY-MODEL.md](./ARCHITECTURE/CONSISTENCY-MODEL.md) | Write atomicity and failure recovery |
| [CONCURRENCY-CONTROL.md](./ARCHITECTURE/CONCURRENCY-CONTROL.md) | Optimistic concurrency with CAS |
| [REVISION-ID-STRATEGY.md](./ARCHITECTURE/REVISION-ID-STRATEGY.md) | Monotonic per-entity revision IDs |
| [CACHING-STRATEGY.md](./ARCHITECTURE/CACHING-STRATEGY.md) | CDN and object cache design |
| [CHANGE-NOTIFICATION.md](./ARCHITECTURE/CHANGE-NOTIFICATION.md) | Event streaming and consumers |
| [SCHEMA-EVOLUTION.md](./ARCHITECTURE/SCHEMA-EVOLUTION.md) | Schema versioning and migration |
| [ENTITY-DELETION.md](./ARCHITECTURE/ENTITY-DELETION.md) | Soft and hard delete semantics |
| [BULK-OPERATIONS.md](./ARCHITECTURE/BULK-OPERATIONS.md) | Import and export operations |

## Additional Resources

- [MIGRATION-STRATEGY.md](./MIGRATION-STRATEGY.md) - Migration approach from existing Wikibase deployments
- [SCALING-PROPERTIES.md](./SCALING-PROPERTIES.md) - System scaling characteristics and bottlenecks

## Design Philosophy

This architecture embraces:

- **Immutability**: All content is stored as immutable snapshots
- **Eventual consistency**: With reconciliation guarantees and no data loss
- **Horizontal scalability**: S3 for storage, Vitess for indexing
- **Auditability**: Perfect revision history by design
- **Decoupling**: MediaWiki becomes a stateless API client

## Getting Started

Start with [ARCHITECTURE.md](./ARCHITECTURE/ARCHITECTURE.md) for the complete architecture overview, then explore the specific topic documents for deeper dives into each area.
