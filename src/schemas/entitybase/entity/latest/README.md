# Entity Response Schema

This schema defines the structure for single entity API responses from EntityBase. Terms (labels, descriptions, aliases) are returned with hashes for deduplication; full values are fetched separately via metadata endpoints.

## Mock Example
```json
{
  "id": "Q42",
  "type": "item",
  "labels": {"en": {"language": "en", "hash": 987654321}},
  "claims": {"P31": [{"mainsnak": {"property": "P31", "datatype": "wikibase-item"}}]}
}
```