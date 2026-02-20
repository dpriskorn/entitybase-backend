# Entitybase Backend

Welcome to Entitybase — a clean-room, billion-scale Wikibase backend built for speed, scalability, and correctness.

## What is Entitybase?

Entitybase is a high-performance backend designed to hold metadata about all of the world's knowledge (Wikibase). It provides a REST API for managing structured knowledge — items, properties, and lexemes — with full support for labels, descriptions, aliases, statements, and complete revision history.

Designed for **1 billion+ entities** and **1 trillion unique statements**, it stores every edit as an immutable snapshot in S3, with Vitess handling fast lookups and indexing.

## Key Features

- **Immutable Revisions** — Every edit creates an immutable snapshot in S3; nothing is ever overwritten
- **122 REST Endpoints** — Full CRUD for entities, terms, statements, users, and more
- **Complete Lexeme Support** — Forms, senses, lemmas, glosses, and lexical categories
- **Statement Deduplication** — Hash-based storage reduces storage while enabling analytics
- **RDF Export** — Turtle format
- **Entity Protection** — Full locks, semi-protection, archiving, and mass-edit protection
- **User Features** — Watchlists, endorsements, thanks, and activity tracking
- **Horizontal Scaling** — Vitess sharding + S3 for infinite scale

## Comparison with Wikibase Suite

| Feature | Entitybase | Wikibase Suite |
|---------|------------|----------------|
| **Capacity** | 1B+ entities, 1T+ statements | ~100M entities (Wikidata) |
| **Storage** | Immutable S3 snapshots + Vitess | MySQL + blob storage |
| **Statement Deduplication** | Hash-based (~50%+ storage reduction) | None |
| **JSON Output** | `/entities/{id}.json` | `wbgetentities` API |
| **TTL Output** | Turtle (alpha) | Full support |
| **RDF/XML** | Not planned | Supported |
| **NTriples** | Not planned | Supported |
| **Change Streaming** | RDF change events (alpha) | None |
| **Batch Updates** | No (separate calls) | Yes (single API call) |

> **Note**: Entitybase is in alpha. Wikibase Suite is production-ready.

## Architecture

```
Client → REST API → Service Layer → Repository Layer
                                      ↓
                           ┌───────────┴───────────┐
                           │   Storage Stack      │
                           │  S3 (Snapshots)      │
                           │  Vitess (Indexing)   │
                           └──────────────────────┘
```

## Explore

- [Getting Started](GETTING_STARTED.md) — Quick start guide
- [Setup](SETUP.md) — Environment setup
- [Project Structure](PROJECT_STRUCTURE.md) — Codebase overview
- [Architecture](ARCHITECTURE/ARCHITECTURE.md) — Deep dive into system design
- [Features](features/ENDPOINTS.md) — API endpoints, statement deduplication, bulk operations
- [Wikidata](WIKIDATA/README.md) — Wikidata integration
- [Diagrams](DIAGRAMS/index.md) — Visual architecture
