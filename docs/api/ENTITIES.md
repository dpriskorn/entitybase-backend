# Entities API

> API endpoints for general entity operations (works for all entity types)

---

## GET /v1/entities/{entity_id}
**Get Entity**

Retrieve a single entity by its ID.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_entity_v1_entities__entity_id__get` |
| Method | `GET` |
| Path | `/v1/entities/{entity_id}` |
| Parameters | `entity_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## DELETE /v1/entities/{entity_id}
**Delete Entity**

Delete an entity.

| Aspect | Details |
|--------|---------|
| Operation ID | `delete_entity_v1_entities__entity_id__delete` |
| Method | `DELETE` |
| Path | `/v1/entities/{entity_id}` |
| Parameters | `entity_id` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[EntityDeleteRequest](#entitydeleterequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## JSON & Turtle Exports

### GET /v1/entities/{entity_id}.json
**Get Entity Data Json**

Get entity data in JSON format.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_entity_data_json_v1_entities__entity_id__json_get` |
| Method | `GET` |
| Path | `/v1/entities/{entity_id}.json` |
| Parameters | `entity_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### GET /v1/entities/{entity_id}.ttl
**Get Entity Data Turtle**

Get entity data in Turtle format.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_entity_data_turtle_v1_entities__entity_id__ttl_get` |
| Method | `GET` |
| Path | `/v1/entities/{entity_id}.ttl` |
| Parameters | `entity_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## Labels

### GET /v1/entities/{entity_id}/labels/{language_code}
**Get Entity Label**

Get entity label text for language.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_entity_label_v1_entities__entity_id__labels__language_code__get` |
| Method | `GET` |
| Path | `/v1/entities/{entity_id}/labels/{language_code}` |
| Parameters | `entity_id` (path, Required) `language_code` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### POST /v1/entities/{entity_id}/labels/{language_code}
**Add Entity Label**

Add a new label to entity for language (alias for PUT).

| Aspect | Details |
|--------|---------|
| Operation ID | `add_entity_label_v1_entities__entity_id__labels__language_code__post` |
| Method | `POST` |
| Path | `/v1/entities/{entity_id}/labels/{language_code}` |
| Parameters | `entity_id` (path, Required) `language_code` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) |
| Request Body | `[TermUpdateRequest](#termupdaterequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### PUT /v1/entities/{entity_id}/labels/{language_code}
**Update Entity Label**

Update entity label for language.

| Aspect | Details |
|--------|---------|
| Operation ID | `update_entity_label_v1_entities__entity_id__labels__language_code__put` |
| Method | `PUT` |
| Path | `/v1/entities/{entity_id}/labels/{language_code}` |
| Parameters | `entity_id` (path, Required) `language_code` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) |
| Request Body | `[TermUpdateRequest](#termupdaterequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### DELETE /v1/entities/{entity_id}/labels/{language_code}
**Delete Entity Label**

Delete entity label for language.

| Aspect | Details |
|--------|---------|
| Operation ID | `delete_entity_label_v1_entities__entity_id__labels__language_code__delete` |
| Method | `DELETE` |
| Path | `/v1/entities/{entity_id}/labels/{language_code}` |
| Parameters | `entity_id` (path, Required) `language_code` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## Descriptions

### GET /v1/entities/{entity_id}/descriptions/{language_code}
**Get Entity Description**

Get entity description text for language.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_entity_description_v1_entities__entity_id__descriptions__language_code__get` |
| Method | `GET` |
| Path | `/v1/entities/{entity_id}/descriptions/{language_code}` |
| Parameters | `entity_id` (path, Required) `language_code` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### PUT /v1/entities/{entity_id}/descriptions/{language_code}
**Update Entity Description**

Update entity description for language.

| Aspect | Details |
|--------|---------|
| Operation ID | `update_entity_description_v1_entities__entity_id__descriptions__language_code__put` |
| Method | `PUT` |
| Path | `/v1/entities/{entity_id}/descriptions/{language_code}` |
| Parameters | `entity_id` (path, Required) `language_code` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) |
| Request Body | `[TermUpdateRequest](#termupdaterequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### DELETE /v1/entities/{entity_id}/descriptions/{language_code}
**Delete Entity Description**

Delete entity description for language.

| Aspect | Details |
|--------|---------|
| Operation ID | `delete_entity_description_v1_entities__entity_id__descriptions__language_code__delete` |
| Method | `DELETE` |
| Path | `/v1/entities/{entity_id}/descriptions/{language_code}` |
| Parameters | `entity_id` (path, Required) `language_code` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## Aliases

### GET /v1/entities/{entity_id}/aliases/{language_code}
**Get Entity Aliases**

Get entity alias texts for language.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_entity_aliases_v1_entities__entity_id__aliases__language_code__get` |
| Method | `GET` |
| Path | `/v1/entities/{entity_id}/aliases/{language_code}` |
| Parameters | `entity_id` (path, Required) `language_code` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### POST /v1/entities/{entity_id}/aliases/{language_code}
**Add Entity Alias**

Add a single alias to entity for language.

| Aspect | Details |
|--------|---------|
| Operation ID | `add_entity_alias_v1_entities__entity_id__aliases__language_code__post` |
| Method | `POST` |
| Path | `/v1/entities/{entity_id}/aliases/{language_code}` |
| Parameters | `entity_id` (path, Required) `language_code` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) |
| Request Body | `[TermUpdateRequest](#termupdaterequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### PUT /v1/entities/{entity_id}/aliases/{language_code}
**Update Entity Aliases**

Update entity aliases for language.

| Aspect | Details |
|--------|---------|
| Operation ID | `update_entity_aliases_v1_entities__entity_id__aliases__language_code__put` |
| Method | `PUT` |
| Path | `/v1/entities/{entity_id}/aliases/{language_code}` |
| Parameters | `entity_id` (path, Required) `language_code` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) |
| Request Body | Inline schema |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### DELETE /v1/entities/{entity_id}/aliases/{language_code}
**Delete Entity Aliases**

Delete all aliases for entity language.

| Aspect | Details |
|--------|---------|
| Operation ID | `delete_entity_aliases_v1_entities__entity_id__aliases__language_code__delete` |
| Method | `DELETE` |
| Path | `/v1/entities/{entity_id}/aliases/{language_code}` |
| Parameters | `entity_id` (path, Required) `language_code` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## Statements

### POST /v1/entities/{entity_id}/statements
**Add Entity Statement**

Add a single statement to an entity.

| Aspect | Details |
|--------|---------|
| Operation ID | `add_entity_statement_v1_entities__entity_id__statements_post` |
| Method | `POST` |
| Path | `/v1/entities/{entity_id}/statements` |
| Parameters | `entity_id` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) |
| Request Body | `[AddStatementRequest](#addstatementrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### PATCH /v1/entities/{entity_id}/statements/{statement_hash}
**Patch Entity Statement**

Replace a statement by hash with new claim data.

| Aspect | Details |
|--------|---------|
| Operation ID | `patch_entity_statement_v1_entities__entity_id__statements__statement_hash__patch` |
| Method | `PATCH` |
| Path | `/v1/entities/{entity_id}/statements/{statement_hash}` |
| Parameters | `entity_id` (path, Required) `statement_hash` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) |
| Request Body | `[PatchStatementRequest](#patchstatementrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### DELETE /v1/entities/{entity_id}/statements/{statement_hash}
**Remove Entity Statement**

Remove a statement by hash from an entity.

| Aspect | Details |
|--------|---------|
| Operation ID | `remove_entity_statement_v1_entities__entity_id__statements__statement_hash__delete` |
| Method | `DELETE` |
| Path | `/v1/entities/{entity_id}/statements/{statement_hash}` |
| Parameters | `entity_id` (path, Required) `statement_hash` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) |
| Request Body | `[RemoveStatementRequest](#removestatementrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## Properties

### GET /v1/entities/{entity_id}/properties
**Get Entity Properties**

Get list of unique property IDs for an entity's head revision.

Returns sorted list of properties used in entity statements.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_entity_properties_v1_entities__entity_id__properties_get` |
| Method | `GET` |
| Path | `/v1/entities/{entity_id}/properties` |
| Parameters | `entity_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### GET /v1/entities/{entity_id}/property_counts
**Get Entity Property Counts**

Get statement counts per property for an entity's head revision.

Returns dict mapping property ID -> count of statements.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_entity_property_counts_v1_entities__entity_id__property_counts_get` |
| Method | `GET` |
| Path | `/v1/entities/{entity_id}/property_counts` |
| Parameters | `entity_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## Sitelinks

### GET /v1/entities/{entity_id}/sitelinks
**Get All Sitelinks**

Get all sitelinks for an entity.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_all_sitelinks_v1_entities__entity_id__sitelinks_get` |
| Method | `GET` |
| Path | `/v1/entities/{entity_id}/sitelinks` |
| Parameters | `entity_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### GET /v1/entities/{entity_id}/sitelinks/{site}
**Get Entity Sitelink**

Get a single sitelink for an entity.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_entity_sitelink_v1_entities__entity_id__sitelinks__site__get` |
| Method | `GET` |
| Path | `/v1/entities/{entity_id}/sitelinks/{site}` |
| Parameters | `entity_id` (path, Required) `site` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### POST /v1/entities/{entity_id}/sitelinks/{site}
**Post Entity Sitelink**

Add a new sitelink for an entity.

| Aspect | Details |
|--------|---------|
| Operation ID | `post_entity_sitelink_v1_entities__entity_id__sitelinks__site__post` |
| Method | `POST` |
| Path | `/v1/entities/{entity_id}/sitelinks/{site}` |
| Parameters | `entity_id` (path, Required) `site` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) |
| Request Body | `[SitelinkData](#sitelinkdata)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### PUT /v1/entities/{entity_id}/sitelinks/{site}
**Put Entity Sitelink**

Update an existing sitelink for an entity.

| Aspect | Details |
|--------|---------|
| Operation ID | `put_entity_sitelink_v1_entities__entity_id__sitelinks__site__put` |
| Method | `PUT` |
| Path | `/v1/entities/{entity_id}/sitelinks/{site}` |
| Parameters | `entity_id` (path, Required) `site` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) |
| Request Body | `[SitelinkData](#sitelinkdata)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### DELETE /v1/entities/{entity_id}/sitelinks/{site}
**Delete Entity Sitelink**

Delete a sitelink from an entity.

| Aspect | Details |
|--------|---------|
| Operation ID | `delete_entity_sitelink_v1_entities__entity_id__sitelinks__site__delete` |
| Method | `DELETE` |
| Path | `/v1/entities/{entity_id}/sitelinks/{site}` |
| Parameters | `entity_id` (path, Required) `site` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## Revisions

### GET /v1/entities/{entity_id}/revisions
**Get Entity History**

Get the revision history for an entity.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_entity_history_v1_entities__entity_id__revisions_get` |
| Method | `GET` |
| Path | `/v1/entities/{entity_id}/revisions` |
| Parameters | `entity_id` (path, Required) `limit` (query, Optional) `offset` (query, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### GET /v1/entities/{entity_id}/revision/{revision_id}
**Get Entity Revision**

Get a specific revision of an entity.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_entity_revision_v1_entities__entity_id__revision__revision_id__get` |
| Method | `GET` |
| Path | `/v1/entities/{entity_id}/revision/{revision_id}` |
| Parameters | `entity_id` (path, Required) `revision_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### GET /v1/entities/{entity_id}/revision/{revision_id}/json
**Get Entity Json Revision**

Get JSON representation of a specific entity revision.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_entity_json_revision_v1_entities__entity_id__revision__revision_id__json_get` |
| Method | `GET` |
| Path | `/v1/entities/{entity_id}/revision/{revision_id}/json` |
| Parameters | `entity_id` (path, Required) `revision_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### POST /v1/entities/{entity_id}/revert
**Revert Entity**

Revert entity to a previous revision.

| Aspect | Details |
|--------|---------|
| Operation ID | `revert_entity_v1_entities__entity_id__revert_post` |
| Method | `POST` |
| Path | `/v1/entities/{entity_id}/revert` |
| Parameters | `entity_id` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) |
| Request Body | `[EntityRevertRequest](#entityrevertrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## Entity Protection

### POST /v1/entities/{entity_id}/lock
**Lock Entity**

Lock an entity from edits.

| Aspect | Details |
|--------|---------|
| Operation ID | `lock_entity_v1_entities__entity_id__lock_post` |
| Method | `POST` |
| Path | `/v1/entities/{entity_id}/lock` |
| Parameters | `entity_id` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) |
| Request Body | `[EntityStatusRequest](#entitystatusrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### DELETE /v1/entities/{entity_id}/lock
**Unlock Entity**

Remove lock from an entity.

| Aspect | Details |
|--------|---------|
| Operation ID | `unlock_entity_v1_entities__entity_id__lock_delete` |
| Method | `DELETE` |
| Path | `/v1/entities/{entity_id}/lock` |
| Parameters | `entity_id` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) |
| Request Body | `[EntityStatusRequest](#entitystatusrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### POST /v1/entities/{entity_id}/archive
**Archive Entity**

Archive an entity.

| Aspect | Details |
|--------|---------|
| Operation ID | `archive_entity_v1_entities__entity_id__archive_post` |
| Method | `POST` |
| Path | `/v1/entities/{entity_id}/archive` |
| Parameters | `entity_id` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) |
| Request Body | `[EntityStatusRequest](#entitystatusrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### DELETE /v1/entities/{entity_id}/archive
**Unarchive Entity**

Unarchive an entity.

| Aspect | Details |
|--------|---------|
| Operation ID | `unarchive_entity_v1_entities__entity_id__archive_delete` |
| Method | `DELETE` |
| Path | `/v1/entities/{entity_id}/archive` |
| Parameters | `entity_id` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) |
| Request Body | `[EntityStatusRequest](#entitystatusrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### POST /v1/entities/{entity_id}/semi-protect
**Semi Protect Entity**

Semi-protect an entity.

| Aspect | Details |
|--------|---------|
| Operation ID | `semi_protect_entity_v1_entities__entity_id__semi_protect_post` |
| Method | `POST` |
| Path | `/v1/entities/{entity_id}/semi-protect` |
| Parameters | `entity_id` (path, Required) |
| Request Body | `[EntityStatusRequest](#entitystatusrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### DELETE /v1/entities/{entity_id}/semi-protect
**Unsemi Protect Entity**

Remove semi-protection from an entity.

| Aspect | Details |
|--------|---------|
| Operation ID | `unsemi_protect_entity_v1_entities__entity_id__semi_protect_delete` |
| Method | `DELETE` |
| Path | `/v1/entities/{entity_id}/semi-protect` |
| Parameters | `entity_id` (path, Required) |
| Request Body | `[EntityStatusRequest](#entitystatusrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### POST /v1/entities/{entity_id}/mass-edit-protect
**Mass Edit Protect Entity**

Add mass edit protection to an entity.

| Aspect | Details |
|--------|---------|
| Operation ID | `mass_edit_protect_entity_v1_entities__entity_id__mass_edit_protect_post` |
| Method | `POST` |
| Path | `/v1/entities/{entity_id}/mass-edit-protect` |
| Parameters | `entity_id` (path, Required) |
| Request Body | `[EntityStatusRequest](#entitystatusrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### DELETE /v1/entities/{entity_id}/mass-edit-protect
**Mass Edit Unprotect Entity**

Remove mass edit protection from an entity.

| Aspect | Details |
|--------|---------|
| Operation ID | `mass_edit_unprotect_entity_v1_entities__entity_id__mass_edit_protect_delete` |
| Method | `DELETE` |
| Path | `/v1/entities/{entity_id}/mass-edit-protect` |
| Parameters | `entity_id` (path, Required) |
| Request Body | `[EntityStatusRequest](#entitystatusrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## Backlinks

### GET /v1/entities/{entity_id}/backlinks
**Get Entity Backlinks**

Get backlinks for an entity.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_entity_backlinks_v1_entities__entity_id__backlinks_get` |
| Method | `GET` |
| Path | `/v1/entities/{entity_id}/backlinks` |
| Parameters | `entity_id` (path, Required) `limit` (query, Optional) `offset` (query, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## Related Links

- [← Back to API](../API.md)
- [Items API](./ITEMS.md)
- [Properties API](./PROPERTIES.md)
- [Lexemes API](./LEXEMES.md)
- [Statements API](./STATEMENTS.md)