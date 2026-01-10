# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Breaking Changes
- **API Endpoints**: Replaced generic `/entity` endpoints with type-specific endpoints
  - Removed: `POST /entity`, `PUT /entity/{id}`, `GET /entity/{id}`
  - Added: Type-specific endpoints for items, properties, lexemes, and entity schemas
- **Entity ID Enumeration**: Implemented permanent ID assignment system
  - IDs are never reused, even after entity deletion
  - New entities auto-assign next available ID for their type

### Added
- **Concurrency Protection**: Implemented Compare-And-Swap (CAS) for all Vitess write operations
  - Revision updates/deletions and redirect modifications now use CAS
  - Prevents lost updates during concurrent modifications
  - Returns HTTP 409 on concurrent modification conflicts
  - Added unit tests for CAS success and failure scenarios
- **Type-Specific Endpoints**:
  - `POST /item` - Create new item (Q ID)
  - `GET /item/Q{id}` - Get item
  - `PUT /item/Q{id}` - Update item
  - `DELETE /item/Q{id}` - Delete item
  - `POST /property` - Create new property (P ID)
  - `GET /property/P{id}` - Get property
  - `PUT /property/P{id}` - Update property
  - `DELETE /property/P{id}` - Delete property
  - `POST /lexeme` - Create new lexeme (L ID)
  - `GET /lexeme/L{id}` - Get lexeme
  - `PUT /lexeme/L{id}` - Update lexeme
  - `DELETE /lexeme/L{id}` - Delete lexeme
  - `POST /entityschema` - Create new entity schema (E ID)
  - `GET /entityschema/E{id}` - Get entity schema
  - `PUT /entityschema/E{id}` - Update entity schema
  - `DELETE /entityschema/E{id}` - Delete entity schema

- **Scalable Entity ID Enumeration System**:
  - Range-based ID allocation to prevent write hotspots
  - Configurable worker architecture for horizontal scaling
  - Permanent ID allocation (no reuse, even after deletion)
  - Support for 777K+ entities/day growth rate
  - Database-backed range management with atomic operations

- **Worker Service Architecture**:
  - Dedicated ID generation workers with Docker containerization
  - Configurable worker count for scaling (starts with 1 worker)
  - Health checks and monitoring for worker instances
  - Range pre-allocation to minimize latency

### Changed
- **Schema Version Configuration**: Shortened parameter names
  - `s3_revision_schema_version` → `s3_revision_version`
  - `s3_statement_schema_version` → `s3_statement_version`
  - `wmf_recentchange_schema_version` → `wmf_recentchange_version`

### Technical Details
- **Database Changes**: Added `entity_id_counters` table for ID management
- **Handler Architecture**: Split EntityHandler into separate CRUD classes
- **File Organization**: Moved handlers to type-specific subdirectories</content>
<parameter name="filePath">CHANGELOG.md