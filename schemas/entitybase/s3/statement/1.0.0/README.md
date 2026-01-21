# S3 Statement Snapshot Schema

This schema defines the structure for immutable statement snapshots stored in S3. Statements are stored with hash-based deduplication and full revision tracking.

## Mock Example
```json
{
  "schema_version": "1.0.0",
  "content_hash": 1234567890123456789,
  "statement": {
    "mainsnak": {
      "snaktype": "value",
      "property": "P31",
      "datatype": "wikibase-item"
    },
    "type": "statement",
    "rank": "normal",
    "qualifiers": 9876543210987654321,
    "references": [1234567890123456789, 9876543210987654321]
  },
  "created_at": "2026-01-05T10:00:00Z"
}
```