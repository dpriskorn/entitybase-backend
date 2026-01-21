# S3 Qualifier Snapshot Schema

This schema defines the structure for immutable qualifier snapshots stored in S3. Qualifiers are stored with hash-based deduplication and full revision tracking.

## Mock Example
```json
{
  "schema_version": "1.0.0",
  "content_hash": 1234567890123456789,
  "qualifier": {
    "P31": [
      {
        "snaktype": "value",
        "property": "P31",
        "datatype": "wikibase-item",
        "hash": "abc123"
      }
    ],
    "P569": [
      {
        "snaktype": "value",
        "property": "P569",
        "datatype": "time",
        "hash": "def456"
      }
    ]
  },
  "created_at": "2026-01-05T10:00:00Z"
}
```