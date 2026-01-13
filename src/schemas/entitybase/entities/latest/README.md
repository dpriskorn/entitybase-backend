# Entities List Response Schema

This schema defines the structure for entities list API responses from EntityBase. Terms (labels, descriptions, aliases) are returned with hashes for deduplication; full values are fetched separately via metadata endpoints.

## Mock Example
```json
{
  "entities": {
    "Q42": {
      "id": "Q42",
      "type": "item",
      "labels": {"en": {"language": "en", "hash": 987654321}}
    }
  }
}
```