# S3 Reference Snapshot Schema

This schema defines the structure for immutable reference snapshots stored in S3. References are stored with hash-based deduplication and full revision tracking.

## Mock Example
```json
{
  "schema_version": "1.0.0",
  "content_hash": 1234567890123456789,
  "reference": {
    "hash": "ref123",
    "snaks": {
      "P31": [
        {
          "snaktype": "value",
          "property": "P31",
          "datatype": "wikibase-item",
          "hash": "abc123"
        }
      ]
    },
    "snaks-order": ["P31"]
  },
  "created_at": "2026-01-05T10:00:00Z"
}
```