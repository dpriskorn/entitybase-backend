# Release v1.0.0-alpha1

**Release Date**: 2026-02-17

## About This Release

Entitybase Backend is a clean-room, billion-scale Wikibase JSON and RDF schema compatible backend architecture based on immutable S3 snapshots and Vitess indexing. This is the first alpha release providing core functionality for entity management.

## What's New

### Core Architecture
- Immutable S3 revision storage (no mutable revisions, no diff storage)
- FastAPI REST API with full Wikibase-compatible endpoints
- Vitess database indexing for billion-scale operations
- Statement deduplication system

### Supported Entity Types
- **Items** (Q-ids): Full CRUD operations
- **Properties** (P-ids): Full CRUD operations
- **Lexemes** (L-ids): Full CRUD with forms, senses, glosses, lemmas

### API Features
- Terms management: labels, descriptions, aliases in multiple languages
- Statement management with reference and qualifier support
- Sitelinks support
- Entity revision history
- RDF/SPARQL endpoint
- JSON dump export

### Infrastructure Components
- **API Service**: FastAPI REST API
- **ID Generator Worker**: Range-based ID allocation (supports 777K+ entities/day)
- **JSON Dump Worker**: Entity export in JSON Lines format
- **TTL Dump Worker**: RDF dump generation

## Limitations (v1.0.0-alpha)

- **No authentication**: API is currently open; no user auth or authorization
- **Untested at Wikidata scale**: Works correctly in test environments but has not been validated with full Wikidata-sized datasets

## Testing

All test suites passing:
- Unit tests
- Integration tests
- E2E (end-to-end) tests
- Contract tests (API schema validation)

## Getting Started

See [README.md](README.md) for setup instructions.

## What's Next

- Authentication and authorization
- Production scale testing with Wikidata-sized datasets
- Dump Worker service for RDF dump generation
- Monitoring and metrics for worker health
