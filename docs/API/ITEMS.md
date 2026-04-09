# Items API

> API endpoints for Item entities (Q IDs)

---

## POST /v1/entities/items
**Create Item**

Create a new empty item entity.

| Aspect | Details |
|--------|---------|
| Operation ID | `create_item_v1_entities_items_post` |
| Method | `POST` |
| Path | `/v1/entities/items` |
| Parameters | `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## GET /v1/entities/items/{id}
**Get Item**

Retrieve an item by ID.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_item_v1_entities_items__id_get` |
| Method | `GET` |
| Path | `/v1/entities/items/{id}` |
| Parameters | `id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## DELETE /v1/entities/items/{id}
**Delete Item**

Delete an item by ID.

| Aspect | Details |
|--------|---------|
| Operation ID | `delete_item_v1_entities_items__id_delete` |
| Method | `DELETE` |
| Path | `/v1/entities/items/{id}` |
| Parameters | `id` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## GET /v1/entities/items/{id}/revisions
**Get Item Revisions**

List all revisions for an item.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_item_revisions_v1_entities_items__id__revisions_get` |
| Method | `GET` |
| Path | `/v1/entities/items/{id}/revisions` |
| Parameters | `id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## GET /v1/entities/items/{id}/terms
**Get Item Terms**

Get labels, descriptions, and aliases for an item.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_item_terms_v1_entities_items__id__terms_get` |
| Method | `GET` |
| Path | `/v1/entities/items/{id}/terms` |
| Parameters | `id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## PUT /v1/entities/items/{id}/labels/{lang}
**Add Item Label**

Add or update a label for an item in a specific language.

| Aspect | Details |
|--------|---------|
| Operation ID | `add_item_label_v1_entities_items__id__labels__lang_put` |
| Method | `PUT` |
| Path | `/v1/entities/items/{id}/labels/{lang}` |
| Parameters | `id` (path, Required) `lang` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) |
| Request Body | `[TermUpdateRequest](#termupdaterequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## Related Links

- [← Back to API](../API.md)
- [Properties API](./PROPERTIES.md)
- [Lexemes API](./LEXEMES.md)
- [Entities API](./ENTITIES.md)