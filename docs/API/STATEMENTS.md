# Statements API

> API endpoints for statement operations and deduplication

---

## GET /v1/statements/batch
**Get Batch Statements**

Get statement hashes for multiple entities.

Query params:
- entity_ids: Comma-separated entity IDs (e.g., Q1,Q2,Q3). Max 20.
- property_ids: Optional comma-separated property IDs to filter (e.g., P31,P279).

Returns dict mapping entity_id → property_id → list of statement hashes.
Entities not found return empty dict for that entity_id.

Example: GET /statements/batch?entity_ids=Q1,Q2&property_ids=P31
Returns: {"Q1": {"P31": [123, 456]}, "Q2": {"P31": [789]}}

| Aspect | Details |
|--------|---------|
| Operation ID | `get_batch_statements_v1_statements_batch_get` |
| Method | `GET` |
| Path | `/v1/statements/batch` |
| Parameters | `entity_ids` (query, Required) `property_ids` (query, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## GET /v1/statements/most_used
**Get Most Used Statements**

Get most used statements based on reference count.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_most_used_statements_v1_statements_most_used_get` |
| Method | `GET` |
| Path | `/v1/statements/most_used` |
| Parameters | `limit` (query, Optional) `min_ref_count` (query, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## GET /v1/statements/{content_hash}
**Get Statement**

Retrieve a single statement by its content hash.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_statement_v1_statements__content_hash__get` |
| Method | `GET` |
| Path | `/v1/statements/{content_hash}` |
| Parameters | `content_hash` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## POST /v1/statements/cleanup-orphaned
**Cleanup Orphaned Statements**

Clean up orphaned statements that are no longer referenced.

| Aspect | Details |
|--------|---------|
| Operation ID | `cleanup_orphaned_statements_v1_statements_cleanup_orphaned_post` |
| Method | `POST` |
| Path | `/v1/statements/cleanup-orphaned` |
| Request Body | `[CleanupOrphanedRequest](#cleanuporphanedrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## Related Links

- [← Back to API](../API.md)
- [Entities API](./ENTITIES.md)
- [Statistics API](./STATISTICS.md)