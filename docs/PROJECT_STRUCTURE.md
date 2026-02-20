# Project Structure

Overview of the Entitybase Backend codebase.

## Directory Layout

```
src/models/
├── config/           # Configuration and settings
├── data/             # Data models (Pydantic)
│   ├── config/       # Data config models
│   ├── infrastructure# Infra data models (S3, Vitess records)
│   ├── rest_api/     # API request/response models
│   └── workers/      # Worker data models
├── infrastructure/   # External service integrations
│   ├── s3/           # S3 storage client
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
schemas/              # JSON schemas for S3 data formats
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
- **Storage**: S3 (immutable revisions)
- **Validation**: Pydantic v2
