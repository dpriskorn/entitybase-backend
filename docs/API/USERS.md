# Users API

> API endpoints for user management

---

## POST /v1/users
**Create User**

Create a new user.

| Aspect | Details |
|--------|---------|
| Operation ID | `create_user_v1_users_post` |
| Method | `POST` |
| Path | `/v1/users` |
| Request Body | `[UserCreateRequest](#usercreaterequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## GET /v1/users/{user_id}
**Get User**

Get user information by MediaWiki user ID.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_user_v1_users__user_id__get` |
| Method | `GET` |
| Path | `/v1/users/{user_id}` |
| Parameters | `user_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## DELETE /v1/users/{user_id}
**Delete User**

Delete a user by ID.

| Aspect | Details |
|--------|---------|
| Operation ID | `delete_user_v1_users__user_id__delete` |
| Method | `DELETE` |
| Path | `/v1/users/{user_id}` |
| Parameters | `user_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## GET /v1/users/stat
**Get User Stats**

Get user statistics.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_user_stats_v1_users_stat_get` |
| Method | `GET` |
| Path | `/v1/users/stat` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |

---

## GET /v1/users/{user_id}/activity
**Get User Activity**

Get user's activity with filtering.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_user_activity_v1_users__user_id__activity_get` |
| Method | `GET` |
| Path | `/v1/users/{user_id}/activity` |
| Parameters | `user_id` (path, Required) `type` (query, Optional) `hours` (query, Optional) `limit` (query, Optional) `offset` (query, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## PUT /v1/users/{user_id}/watchlist/toggle
**Toggle Watchlist**

Enable or disable watchlist for user.

| Aspect | Details |
|--------|---------|
| Operation ID | `toggle_watchlist_v1_users__user_id__watchlist_toggle_put` |
| Method | `PUT` |
| Path | `/v1/users/{user_id}/watchlist/toggle` |
| Parameters | `user_id` (path, Required) |
| Request Body | `[WatchlistToggleRequest](#watchlisttogglerequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## Related Links

- [← Back to API](../API.md)
- [Watchlist API](./WATCHLIST.md)