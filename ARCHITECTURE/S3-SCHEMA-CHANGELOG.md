# S3 Entity JSON Schema Changes

This document tracks all S3 entity JSON schema version changes for Wikibase immutable revision system.

## Quick Reference

| Version | Date | Type | Status |
|---------|------|------|--------|
| 1.0 | TBD | Major | Draft |

---

## 1.0 - Major

**Status:** Draft

### Changes

- Initial schema definition for entity JSON snapshots stored in S3

### Schema

```json
{
  "schema_version": "1.0",
  "entity": {
    "id": "string",
    "type": "item|property|lexeme",
    "labels": {},
    "descriptions": {},
    "aliases": {},
    "claims": {},
    "sitelinks": {}
  },
  "metadata": {
    "revision_id": "integer",
    "created_at": "ISO8601",
    "author_id": "string",
    "comment": "string",
    "content_hash": "string"
  }
}
```

### Impact

- Readers: Initial implementation
- Writers: Initial implementation
- Migration: N/A (baseline schema)

### Notes

- Establishes canonical JSON format for immutable S3 snapshots
- All entity fields required unless documented as optional
- Deterministic ordering enforced for hash stability
- `revision_id` must be monotonic per entity
- `content_hash` provides integrity verification
- Snapshots are immutable - no modifications allowed
