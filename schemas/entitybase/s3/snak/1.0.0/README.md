# S3 Snak Snapshot Schema

This schema defines the structure for immutable snak snapshots stored in S3. Snaks are deduplicated and stored separately to optimize storage for statements, qualifiers, and references.

## Mock Example
```json
{
  "schema_version": "1.0.0",
  "snak": {
    "snaktype": "value",
    "property": "P31",
    "datatype": "wikibase-item",
    "hash": "ad7d38a03cdd40cdc373de0dc4e7b7fcbccb31d9",
    "datavalue": {
      "value": {
        "entity-type": "item",
        "numeric-id": 5,
        "id": "Q5"
      },
      "type": "wikibase-entityid"
    }
  },
  "created_at": "2026-01-05T10:00:00Z"
}
```

## Real Example from Q42
```json
{
  "schema_version": "1.0.0",
  "snak": {
    "snaktype": "value",
    "property": "P31",
    "hash": "ad7d38a03cdd40cdc373de0dc4e7b7fcbccb31d9",
    "datavalue": {
      "value": {
        "entity-type": "item",
        "numeric-id": 5,
        "id": "Q5"
      },
      "type": "wikibase-entityid"
    },
    "datatype": "wikibase-item"
  },
  "created_at": "2026-01-05T10:00:00Z"
}
```