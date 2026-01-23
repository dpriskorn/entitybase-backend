# S3 Revision Snapshot Schema v4.0.0

This schema defines the structure for immutable revision snapshots stored in S3. Revisions are stored with hash-based deduplication and full revision tracking. Version 4.0.0 adds support for sitelink badges.

## Mock Example
```json
{
  "schema_version": "4.0.0",
  "revision_id": 12345,
  "created_at": "2026-01-05T10:00:00Z",
  "created_by": "user123",
  "entity_type": "item",
  "entity": 9876543210987654321,
  "content_hash": 1234567890123456789,
  "edit_type": "update",
  "is_semi_protected": false,
  "is_locked": false,
  "is_archived": false
}
```