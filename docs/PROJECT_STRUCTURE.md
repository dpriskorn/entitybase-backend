# Project Structure 📁

> Understanding how the Entitybase codebase is organized. Let's make sense of it all!

---

## Architecture in 3 Sentences 🧠

1. **You (clients)** talk to the **REST API** 
2. The API stores data in **MariaDB** (permanent storage) and indexes it in **Vitess** (fast lookups)
3. Everything is built around **immutable revisions** — once written, never changed

---

## The 3 Main Parts 🏗️

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    REST API  │───▶│     S3       │    │   Vitess    │
│  (FastAPI)   │    │  (storage)   │    │  (indexing) │
└─────────────┘    └─────────────┘    └─────────────┘
     │                   │                   │
     │              Immutable            Fast lookups
     │              snapshots            + queries
     │
     ▼
(what you talk to)
```

---

## Directory Layout

```
src/models/
├── config/           # Configuration and settings
├── data/             # Data models (Pydantic)
│   ├── config/       # Data config models
│   ├── infrastructure# Infra data models (Vitess records)
│   ├── rest_api/     # API request/response models
│   └── workers/      # Worker data models
├── infrastructure/   # External service integrations
│   ├── s3/           # Dump upload client (MinIO)
│   ├── stream/       # Event streaming
│   └── vitess/       # Database repositories
├── internal_representation/  # Core domain models
├── json_parser/      # JSON parsing (Wikidata format → internal)
├── rdf_builder/     # RDF generation (internal → Turtle/XML)
├── rest_api/         # FastAPI endpoints and handlers
├── services/         # Business logic layer
├── utils/            # Shared utilities
├── validation/      # Input validation
└── workers/          # Background workers

tests/                # Test suite
docs/                 # Documentation
schemas/              # JSON schemas for data formats
```

## Key Concepts

- **Internal Representation** - Domain models (Entity, Statement, Value)
- **JSON Parser** - Converts Wikidata JSON → Internal models
- **RDF Builder** - Converts Internal models → RDF Turtle/XML
- **Repositories** - Database access layer (Vitess)
- **Services** - Business logic between API and repositories

## Stack

- **API**: FastAPI
- **Database**: Vitess (MySQL sharding)
- **Storage**: MariaDB (revisions, statements, terms)
- **Validation**: Pydantic v2

---

## What Each Part Does 🎯

### `src/models/rest_api/` — The Doorway 🏪

This is what **clients talk to**. It handles:
- HTTP requests and responses
- Input validation
- Error handling

### `src/models/services/` — The Brain 🧠

The **business logic** layer. It:
- Coordinates between API and storage
- Implements core features
- Contains the "rules" of the system

### `src/models/infrastructure/` — The Connectors 🔌

Integrations with **external systems**:
- `s3/` — Talks to MinIO for dump uploads
- `vitess/` — Talks to Vitess for indexing
- `stream/` — Event streaming (change notifications)

### `src/models/internal_representation/` — The Core 💎

The **domain models** — the heart of Entitybase:
- `Entity` — Item, property, or lexeme
- `Statement` — Claims about entities
- `Value` — The actual data (strings, items, dates, etc.)

### `src/models/json_parser/` — The Translator 🌐

Converts **Wikidata JSON format** → **Internal models**

### `src/models/rdf_builder/` — The Exporter 🐢

Converts **Internal models** → **RDF Turtle format** for semantic web

### `src/models/workers/` — The Background Helpers ⚙️

Background jobs that run separately:
- ID generation (creating Q1, P1, etc.)
- Dump generation (exporting all entities)
- RDF streaming (generating RDF changes)

---

## Quick Mapping 🔗

| You want to... | Look in... |
|---------------|------------|
| Add a new API endpoint | `rest_api/` |
| Change how data is stored | `infrastructure/s3/` |
| Change how data is indexed | `infrastructure/vitess/` |
| Add a new entity type | `internal_representation/` |
| Handle Wikidata JSON import | `json_parser/` |
| Add RDF export format | `rdf_builder/` |
| Add a background job | `workers/` |

---

## See Also

- [🚀 Getting Started](../GETTING_STARTED.md) — Quick start
- [📖 Tutorial](../TUTORIAL.md) — Hands-on walkthrough
- [🏗️ Architecture](../ARCHITECTURE/ARCHITECTURE.md) — Deep dive
