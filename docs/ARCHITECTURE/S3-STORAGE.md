# S3 Storage Architecture

This document outlines how Wikibase backend stores data in Amazon S3, including revision snapshots, metadata, and deduplicated content.

## Overview

S3 is used for immutable storage of entity revisions and deduplicated metadata. Data is organized into buckets with structured paths for efficient retrieval.

## Buckets

### wikibase-revisions
Stores entity revision snapshots.

- **Path**: `{entity_id}/{revision_id}`
- **Format**: YAML (schema-validated)
- **Content**: Full entity snapshot with hashes for deduplicated parts (terms, sitelinks, statements)
- **Example**: `Q42/42` contains revision data with `sitelinks_hashes`, `statements_hashes`, etc.

### wikibase-statements
Stores deduplicated statement (claim) data.

- **Path**: `{hash}`
- **Format**: JSON
- **Content**: Statement objects (mainsnak, qualifiers, references)
- **Example**: `123456789` contains `{"mainsnak": {...}, "qualifiers": {...}}`

### wikibase-terms
Stores deduplicated term metadata (labels, descriptions, aliases).

- **Path**: `{language}:{hash}`
- **Format**: Plain UTF-8 text
- **Content**: Raw term value (e.g., "Douglas Adams")
- **Example**: `en:987654321` contains `Douglas Adams`

### wikibase-sitelinks
Stores deduplicated sitelink titles.

- **Path**: `{hash}`
- **Format**: Plain UTF-8 text
- **Content**: Raw title (e.g., "Main Page")
- **Example**: `876543210` contains `Main Page`

### wikibase-dumps
Stores periodic RDF dumps.

- **Path**: `{date}/{entity_id}.ttl`
- **Format**: Turtle RDF
- **Content**: Entity RDF export

## Deduplication

- **Terms/Sitelinks**: Hashed values stored as plain text; revisions reference hashes.
- **Statements**: Hashed and stored as JSON; revisions use `statements_hashes`.
- **Revisions**: Contain minimal entity data + hashes for reconstruction.

## Performance Considerations

- Plain text for terms/sitelinks minimizes size (no JSON overhead).
- Hashes ensure integrity without schemas.
- Batch endpoints reduce round-trips for metadata lookups.