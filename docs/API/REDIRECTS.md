# Redirects API

> API endpoints for entity redirects

---

## POST /v1/redirects
**Create Entity Redirect**

Create a redirect for an entity.

| Aspect | Details |
|--------|---------|
| Operation ID | `create_entity_redirect_v1_redirects_post` |
| Method | `POST` |
| Path | `/v1/redirects` |
| Parameters | `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[EntityRedirectRequest](#entityredirectrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## POST /v1/entities/{entity_id}/revert-redirect
**Revert Entity Redirect**

Revert a redirect back to a normal entity.

| Aspect | Details |
|--------|---------|
| Operation ID | `revert_entity_redirect_v1_entities__entity_id__revert_redirect_post` |
| Method | `POST` |
| Path | `/v1/entities/{entity_id}/revert-redirect` |
| Parameters | `entity_id` (path, Required) `X-User-ID` (header, Required) `X-Edit-Summary` (header, Required) `X-Base-Revision-ID` (header, Optional) |
| Request Body | `[RedirectRevertRequest](#redirectrevertrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## Related Links

- [← Back to API](../API.md)
- [Entities API](./ENTITIES.md)