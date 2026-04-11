# Entitybase Backend 🏗️

> An API-first, billion-scale backend for structured knowledge — items, properties, and statements without the wiki.

## What Problem Does This Solve? 🤔

Imagine you're building the next Wikidata — a database that holds structured knowledge about *everything* in the world. Millions of items, billions of statements, and thousands of edits per second. 😱

**The problem?** Traditional databases overwrite data. When someone edits an item, the old version disappears. You can't easily:
- See who changed what and when
- Roll back to an old version
- Know what changed between two edits
- Trust that your data hasn't been silently modified

**Entitybase solves this** by treating every edit as an immutable snapshot — like Git for structured data. Once written, an edit can never be changed or deleted. Ever. This gives you perfect auditability, easy rollbacks, and rock-solid consistency.

## Who Is This For? 👥

Entitybase is perfect for:

- 🚀 **App developers** — Building apps that need structured knowledge without a full wiki
- 🔬 **Research platforms** — Need a clean API for knowledge graphs and structured data
- 🏛️ **Wikimedia projects** — Want just the data model (entities, statements) without MediaWiki
- 📊 **Data engineers** — Need clean RDF exports of structured knowledge
- 🛠️ **Custom solutions** — Building "knowledge base" apps without wiki overhead

## The 3-Second Pitch 📣

> **Entitybase = Git for structured knowledge**
> 
> Every edit creates an immutable snapshot in S3. Vitess handles fast lookups. REST API gives you full CRUD. Built for 1 billion+ entities and 1 trillion statements.

## TL;DR Quick Facts ⚡

| Capability | Value |
|------------|-------|
| **Interface** | REST API only (no wiki pages) 🏃 |
| **Authentication** | None yet (planned) 🔐 |
| **Capacity** | 1B+ entities 💎 |
| **Statements** | 1T+ unique statements |
| **Revisions** | Immutable (never overwritten) 🔒 |
| **API** | 122 REST endpoints |
| **Storage** | S3 (snapshots) + Vitess (indexing) |
| **Exports** | JSON, Turtle (RDF) 🐢 |
| **Version** | 0.1.0 🚧 |

## Architecture in 3 Boxes 📦

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    You      │───▶│   REST API  │───▶│    S3       │
│  (clients)  │    │  (FastAPI)  │    │  (storage)  │
└─────────────┘    └─────────────┘    └─────────────┘
                           │
                           ▼
                   ┌─────────────┐
                   │   Vitess    │
                   │  (indexing) │
                   └─────────────┘
```

1. **You (clients)** — API calls from your app, scripts, or frontend
2. **REST API (FastAPI)** — Validates, processes, and routes requests
3. **S3 (storage)** — Immutable snapshots of every entity revision
4. **Vitess (indexing)** — Lightning-fast lookups and queries

> 💡 **Think of it like this**: S3 is the permanent record (📜), Vitess is the index in the back of the book (📑), and the API is the librarian (👩‍🏫)

## Key Features ✨

- **Immutable Revisions** — Every edit creates a snapshot you can never overwrite
- **122 REST Endpoints** — Full CRUD for entities, terms, statements, users, and more
- **Complete Lexeme Support** — Forms, senses, lemmas, glosses, and lexical categories
- **Statement Deduplication** — Hash-based storage can reduce storage by 50%+
- **RDF Export** — Turtle format for semantic web integration 🐢
- **Entity Protection** — Full locks, semi-protection, archiving, and mass-edit protection
- **User Features** — Watchlists, endorsements, thanks, and activity tracking
- **Horizontal Scaling** — Vitess sharding + S3 for infinite scale

## Why This Design? 🧠

You might ask: "Why not just use MySQL like everyone else?"

### The Problem with Mutable Data

```
Traditional database:     Entitybase:
┌─────────────┐         ┌─────────────┐
│   Item Q1   │         │ Rev 1: Q1   │──▶ S3 snapshot
│  (current)  │         │ Rev 2: Q1   │──▶ S3 snapshot
└─────────────┘         │ Rev 3: Q1   │──▶ S3 snapshot
  (overwrites!)         └─────────────┘
                         (append-only!)
```

Traditional databases **overwrite** data. You lose history. Entitybase **appends** immutable snapshots. You gain:

- ✅ **Perfect auditability** — Who changed what, when
- ✅ **Easy rollbacks** — Just point to an old revision
- ✅ **No data loss** — Old versions are never deleted
- ✅ **Event sourcing** — Replay events to rebuild state
- ✅ **Conflict resolution** — Compare revisions without locking

### Statement Deduplication

Statements (like "population → 8.9 billion") appear millions of times across entities. Entitybase stores each unique statement once and references it by hash:

```
┌──────────────────┐      ┌──────────────────┐
│  Q1: Earth       │      │ Statement hash   │
│  population: X   │─────▶│ "population:8.9B"│
└──────────────────┘      └──────────────────┘
┌──────────────────┐      (stored once! 💾)
│  Q2: Country     │
│  population: X   │─────▶ Same hash, reuses storage
└──────────────────┘
```

This can reduce storage by 50%+ for typical Wikibase datasets!

## Comparison with Wikibase Suite

| Feature | Entitybase | Wikibase Suite |
|---------|------------|----------------|
| **Interface** | REST API only | REST API + web UI + wiki pages |
| **Wiki pages** | ❌ None | ✅ Article pages, talk pages, user pages |
| **Frontend** | ❌ None | ✅ Wikibase UI (Vue) |
| **Authentication** | ❌ None (planned) | ✅ Full user system |
| **Capacity** | 1B+ entities, 1T+ statements | ~100M entities (Wikidata) |
| **Storage** | Immutable S3 snapshots + Vitess | MySQL + blob storage |
| **Statement Deduplication** | Hash-based (~50%+ storage reduction) | None |
| **JSON Output** | `/entities/{id}.json` | `wbgetentities` API |
| **TTL Output** | Turtle (alpha) | Full support |
| **RDF/XML** | Not planned | Supported |
| **NTriples** | Not planned | Supported |
| **Change Streaming** | RDF change events (alpha) | None |
| **Batch Updates** | No (separate calls) | Yes (single API call) |

> **Note**: Entitybase is an alternative backend for structured data — not a drop-in replacement. Wikibase Suite is production-ready for full wiki sites.

## Explore

- [🚀 Getting Started](GETTING_STARTED.md) — Quick start guide (5 minutes!)
- [📖 Tutorial](TUTORIAL.md) — Hands-on step-by-step walkthrough
- [⚙️ Setup](SETUP.md) — Environment setup
- [📁 Project Structure](PROJECT_STRUCTURE.md) — Codebase overview
- [🏗️ Architecture](ARCHITECTURE/ARCHITECTURE.md) — Deep dive into system design
- [✨ Features](Features/ENDPOINTS.md) — API endpoints, statement deduplication, bulk operations
- [🐢 Wikidata](WIKIDATA/README.md) — Wikidata integration
- [📊 Diagrams](DIAGRAMS/index.md) — Visual architecture
- [🔍 Glossary](GLOSSARY.md) — Domain terms explained
- [⚡ Quick Reference](QUICKREF.md) — One-page command reference
