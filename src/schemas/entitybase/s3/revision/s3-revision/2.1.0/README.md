# S3 Revision Schema v2.1.0

This version introduces full deduplication for entity content, storing only hashes for terms (labels/descriptions/aliases), sitelinks, and statements (claims). The `entity` object is minimal, containing only `id` and `type`.

## Key Changes from v1.2.0
- **Added `sitelinks_hashes`**: Per-wiki hashes for sitelink titles (replaces inline sitelinks).
- **Added `statements_hashes`**: Hashes for statements grouped by property (replaces inline claims).
- **Removed inline content**: `entity` no longer includes `claims`, `labels`, `descriptions`, `aliases`, or `sitelinks`.
- **Deduplication impact**: Revisions are ~90% smaller (e.g., Q42 from 677 KB to ~15 KB), with full content reconstructed from S3 metadata buckets.

## content_hash Field
A Rapidhash integer of the full entity data (pre-deduplication) for change detection and deduplication. Allows quick comparison between revisions without storing full content. Calculated as `rapidhash(entity_json)` in code.

## Mock Example
```json
{
  "schema_version": "2.1.0",
  "revision_id": 42,
  "created_at": "2025-01-13T12:00:00Z",
  "created_by": "user123",
  "entity_type": "item",
  "content_hash": 1234567890123456789,
  "labels_hashes": {"en": 987654321},
  "statements_hashes": {"P31": [876543210]},
  "entity": {"id": "Q42", "type": "item"}
}
```