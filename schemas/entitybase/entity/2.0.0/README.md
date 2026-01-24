# Wikibase Entity Schema 2.0.0

This schema defines a hash-based reference structure for Wikibase entity objects. Instead of storing full inline data, the schema references stored content via hashes, enabling efficient deduplication and storage. All actual content (labels, descriptions, statements, etc.) is stored separately with hash-based references.

## Key Changes from 1.0.0

- **Hash-based references**: All content (labels, descriptions, aliases, statements, sitelinks) uses hash integers instead of inline objects
- **Revision metadata**: Added schema_version, revision_id, timestamps, and status flags
- **Protection and status fields**: Tracks entity protection, locks, archival status, and deletion state
- **Deduplication**: Identical strings across entities share the same hash reference
- **Compact storage**: Reduces duplication by referencing shared content via hashes

## Mock Example

```json
{
  "schema_version": "2.0.0",
  "id": "Q123",
  "type": "item",
  "revision_id": 123456789,
  "created_at": "2026-01-24T19:30:00Z",
  "created_by": "ExampleUser",
  "entity_type": "item",
  "content_hash": 9876543210123456789,
  "is_semi_protected": false,
  "is_locked": false,
  "is_archived": false,
  "is_dangling": false,
  "is_mass_edit_protected": false,
  "deleted": false,
  "labels": {
    "en": 123456789,
    "de": 234567890
  },
  "descriptions": {
    "en": 345678901
  },
  "aliases": {
    "en": [456789012, 567890123]
  },
  "sitelinks": {
    "enwiki": {
      "title_hash": 678901234,
      "badges": []
    }
  },
  "statements": {
    "hashes": [789012345, 890123456]
  }
}
```

## Field Descriptions

### Core Fields
- `schema_version`: Schema version (MAJOR.MINOR.PATCH)
- `id`: Entity identifier (e.g., "Q123", "P456", "L789")
- `type`: Entity type (item, property, lexeme, entityschema)
- `revision_id`: Revision ID
- `created_at`: ISO 8601 timestamp when this revision was created
- `created_by`: User or bot that created this revision
- `entity_type`: Type of entity (item, property, or lexeme)

### Status Fields
- `redirects_to`: Target entity ID if this entity is a redirect (optional)
- `content_hash`: Rapidhash integer for deduplication
- `edit_type`: Text classification of edit type (optional)
- `is_semi_protected`: Entity is semi-protected
- `is_locked`: Entity is locked
- `is_archived`: Entity is archived
- `is_dangling`: Entity is dangling
- `is_mass_edit_protected`: Entity is mass edit protected
- `deleted`: Entity has been deleted
- `deletion_reason`: Reason for deletion (if deleted)
- `deleted_at`: Timestamp when deleted (if deleted)
- `deleted_by`: User that deleted the entity (if deleted)

### Hash References

#### Term References (Labels, Descriptions, Aliases)
- `labels`: Hash references to label strings per language
- `descriptions`: Hash references to description strings per language
- `aliases`: Hash references to alias string arrays per language

#### Sitelinks
- `sitelinks`: Hash references to sitelink data per wiki site
  - References `sitelink/1.0.0` schema
  - Contains `title_hash` and `badges` array

#### Statements
- `statements`: Hash references to statements
  - `hashes`: Flat list of statement hash integers (rapidhash of each statement)
  - Statements reference the `statement/3.0.0` schema
  - Frontend can infer property IDs and counts from statement content

### Lexeme-Specific Fields
- `lemmas`: Hash references to lemma strings (lexeme only)
- `lexicalCategory`: Entity ID for lexical category (e.g., "Q5")
- `language`: Entity ID for language (e.g., "Q1860")
- `forms`: Form data for lexemes
- `senses`: Sense data for lexemes

## Schema Pyramid

```
entity/2.0.0 (user response)
    ↓ references via hashes
revision/4.0.0 (S3 storage)
    ↓
statement/3.0.0, sitelink/1.0.0 (S3 objects)
    ↓
snak/1.0.0, reference/1.0.0, qualifier/1.0.0 (atomic objects)
```

## Usage Example

When a client requests entity Q123:

1. **Fetch revision metadata** from storage:
   - revision_id, created_at, created_by, status flags

2. **Resolve hash references**:
    - labels["en"] = 123456789 → fetch from storage → "Test Item"
    - statements["hashes"] = [789012345] → fetch from S3 → full statement objects

3. **Return combined response** with all references resolved

## Advantages of Hash-Based Storage

- **Deduplication**: Same label/description across entities uses one hash
- **Versioning**: Each hash points to immutable content
- **Compact**: Revision metadata is small; actual content stored efficiently
- **Caching**: Hash-based keys are ideal for CDN/edge caching
- **Comparison**: `content_hash` allows quick equality checks between revisions