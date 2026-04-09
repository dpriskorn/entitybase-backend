# Properties API

> API endpoints for Property entities (P IDs)

---

## POST /v1/entities/properties
**Create Property**

Create a new empty property entity.

| Aspect | Details |
|--------|---------|
| Operation ID | `create_property_v1_entities_properties_post` |
| Method | `POST` |
| Path | `/v1/entities/properties` |
| Parameters | `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## GET /v1/entities/properties/{id}
**Get Property**

Retrieve a property by ID.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_property_v1_entities_properties__id_get` |
| Method | `GET` |
| Path | `/v1/entities/properties/{id}` |
| Parameters | `id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## DELETE /v1/entities/properties/{id}
**Delete Property**

Delete a property by ID.

| Aspect | Details |
|--------|---------|
| Operation ID | `delete_property_v1_entities_properties__id_delete` |
| Method | `DELETE` |
| Path | `/v1/entities/properties/{id}` |
| Parameters | `id` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## GET /v1/entity/{entity_id}/properties/{property_list}
**Get Entity Property Hashes**

Get statement hashes for specified properties in an entity.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_entity_property_hashes_v1_entity__entity_id__properties__property_list__get` |
| Method | `GET` |
| Path | `/v1/entity/{entity_id}/properties/{property_list}` |
| Parameters | `entity_id` (path, Required) `property_list` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## Related Links

- [← Back to API](../API.md)
- [Items API](./ITEMS.md)
- [Lexemes API](./LEXEMES.md)
- [Entities API](./ENTITIES.md)