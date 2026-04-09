# Interactions API

> API endpoints for user interactions (thanks, endorsements)

---

## Thanks

### POST /v1/entities/{entity_id}/revisions/{revision_id}/thank
**Send Thank Endpoint**

Send a thank for a specific revision.

| Aspect | Details |
|--------|---------|
| Operation ID | `send_thank_endpoint_v1_entities__entity_id__revisions__revision_id__thank_post` |
| Method | `POST` |
| Path | `/v1/entities/{entity_id}/revisions/{revision_id}/thank` |
| Parameters | `entity_id` (path, Required) `revision_id` (path, Required) `X-User-ID` (header, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### GET /v1/entities/{entity_id}/revisions/{revision_id}/thanks
**Get Revision Thanks Endpoint**

Get all thanks for a specific revision.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_revision_thanks_endpoint_v1_entities__entity_id__revisions__revision_id__thanks_get` |
| Method | `GET` |
| Path | `/v1/entities/{entity_id}/revisions/{revision_id}/thanks` |
| Parameters | `entity_id` (path, Required) `revision_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### GET /v1/users/{user_id}/thanks/received
**Get Thanks Received Endpoint**

Get thanks received by user.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_thanks_received_endpoint_v1_users__user_id__thanks_received_get` |
| Method | `GET` |
| Path | `/v1/users/{user_id}/thanks/received` |
| Parameters | `user_id` (path, Required) `limit` (query, Optional) `offset` (query, Optional) `hours` (query, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### GET /v1/users/{user_id}/thanks/sent
**Get Thanks Sent Endpoint**

Get thanks sent by user.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_thanks_sent_endpoint_v1_users__user_id__thanks_sent_get` |
| Method | `GET` |
| Path | `/v1/users/{user_id}/thanks/sent` |
| Parameters | `user_id` (path, Required) `limit` (query, Optional) `offset` (query, Optional) `hours` (query, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## Endorsements

### POST /v1/statements/{statement_hash}/endorse
**Endorse Statement Endpoint**

Endorse a statement to signal trust.

| Aspect | Details |
|--------|---------|
| Operation ID | `endorse_statement_endpoint_v1_statements__statement_hash__endorse_post` |
| Method | `POST` |
| Path | `/v1/statements/{statement_hash}/endorse` |
| Parameters | `statement_hash` (path, Required) `X-User-ID` (header, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### DELETE /v1/statements/{statement_hash}/endorse
**Withdraw Endorsement Endpoint**

Withdraw endorsement from a statement.

| Aspect | Details |
|--------|---------|
| Operation ID | `withdraw_endorsement_endpoint_v1_statements__statement_hash__endorse_delete` |
| Method | `DELETE` |
| Path | `/v1/statements/{statement_hash}/endorse` |
| Parameters | `statement_hash` (path, Required) `X-User-ID` (header, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### GET /v1/statements/{statement_hash}/endorsements
**Get Statement Endorsements Endpoint**

Get endorsements for a statement.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_statement_endorsements_endpoint_v1_statements__statement_hash__endorsements_get` |
| Method | `GET` |
| Path | `/v1/statements/{statement_hash}/endorsements` |
| Parameters | `statement_hash` (path, Required) `limit` (query, Optional) `offset` (query, Optional) `include_removed` (query, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### GET /v1/statements/{statement_hash}/endorsements/stats
**Get Statement Endorsement Stats**

Get endorsement statistics for a statement.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_statement_endorsement_stats_v1_statements__statement_hash__endorsements_stats_get` |
| Method | `GET` |
| Path | `/v1/statements/{statement_hash}/endorsements/stats` |
| Parameters | `statement_hash` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### GET /v1/users/{user_id}/endorsements
**Get User Endorsements Endpoint**

Get endorsements given by a user.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_user_endorsements_endpoint_v1_users__user_id__endorsements_get` |
| Method | `GET` |
| Path | `/v1/users/{user_id}/endorsements` |
| Parameters | `user_id` (path, Required) `limit` (query, Optional) `offset` (query, Optional) `include_removed` (query, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### GET /v1/users/{user_id}/endorsements/stats
**Get User Endorsement Stats Endpoint**

Get endorsement statistics for a user.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_user_endorsement_stats_endpoint_v1_users__user_id__endorsements_stats_get` |
| Method | `GET` |
| Path | `/v1/users/{user_id}/endorsements/stats` |
| Parameters | `user_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## Related Links

- [← Back to API](../API.md)
- [Users API](./USERS.md)
- [Statements API](./STATEMENTS.md)