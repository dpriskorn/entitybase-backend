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

- **Entity ID Enumeration System**:
  - Automatic ID assignment for new entities
  - Permanent ID allocation (no reuse)
  - Thread-safe ID generation via database
  - Support for Wikibase ID formats (Q/P/L/E prefixes)

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