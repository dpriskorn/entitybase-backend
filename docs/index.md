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
- **RDF Export** — Turtle, RDF XML, and NTriples formats
- **Entity Protection** — Full locks, semi-protection, archiving, and mass-edit protection
- **User Features** — Watchlists, endorsements, thanks, and activity tracking
- **Horizontal Scaling** — Vitess sharding + S3 for infinite scale

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

- [Architecture](ARCHITECTURE/ARCHITECTURE.md) — Deep dive into system design
- [API Endpoints](ENDPOINTS.md) — Complete REST API reference
- [Wikidata](WIKIDATA/README.md) — Wikidata integration
- [Diagrams](DIAGRAMS/README.md) — Visual architecture
