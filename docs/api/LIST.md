# List API

> API endpoints for listing and searching entities

---

## GET /v1/entities
**List Entities**

List entities based on type, status, edit_type, limit, and offset.

| Aspect | Details |
|--------|---------|
| Operation ID | `list_entities_v1_entities_get` |
| Method | `GET` |
| Path | `/v1/entities` |
| Parameters | `entity_type` (query, Optional) `status` (query, Optional) `edit_type` (query, Optional) `limit` (query, Optional) `offset` (query, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## GET /v1/entities/items
**List Items**

List all items (Q-prefixed entities).

| Aspect | Details |
|--------|---------|
| Operation ID | `list_items_v1_entities_items_get` |
| Method | `GET` |
| Path | `/v1/entities/items` |
| Parameters | `limit` (query, Optional) `offset` (query, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## GET /v1/entities/lexemes
**List Lexemes**

List all lexemes (L-prefixed entities).

| Aspect | Details |
|--------|---------|
| Operation ID | `list_lexemes_v1_entities_lexemes_get` |
| Method | `GET` |
| Path | `/v1/entities/lexemes` |
| Parameters | `limit` (query, Optional) `offset` (query, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## GET /v1/entities/properties
**List Properties**

List all properties (P-prefixed entities).

| Aspect | Details |
|--------|---------|
| Operation ID | `list_properties_v1_entities_properties_get` |
| Method | `GET` |
| Path | `/v1/entities/properties` |
| Parameters | `limit` (query, Optional) `offset` (query, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## Related Links

- [← Back to API](../API.md)
- [Entities API](./ENTITIES.md)