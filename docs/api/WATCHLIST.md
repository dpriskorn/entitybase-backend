# Watchlist API

> API endpoints for user watchlist and notifications

---

## GET /v1/users/{user_id}/watchlist
**Get Watches**

Get user's watchlist.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_watches_v1_users__user_id__watchlist_get` |
| Method | `GET` |
| Path | `/v1/users/{user_id}/watchlist` |
| Parameters | `user_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## POST /v1/users/{user_id}/watchlist
**Add Watch**

Add a watchlist entry for user.

| Aspect | Details |
|--------|---------|
| Operation ID | `add_watch_v1_users__user_id__watchlist_post` |
| Method | `POST` |
| Path | `/v1/users/{user_id}/watchlist` |
| Parameters | `user_id` (path, Required) |
| Request Body | `[WatchlistAddRequest](#watchlistaddrequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## DELETE /v1/users/{user_id}/watchlist/{watch_id}
**Remove Watch By Id**

Remove a watchlist entry by ID.

| Aspect | Details |
|--------|---------|
| Operation ID | `remove_watch_by_id_v1_users__user_id__watchlist__watch_id__delete` |
| Method | `DELETE` |
| Path | `/v1/users/{user_id}/watchlist/{watch_id}` |
| Parameters | `user_id` (path, Required) `watch_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## POST /v1/users/{user_id}/watchlist/remove
**Remove Watch**

Remove a watchlist entry for user.

| Aspect | Details |
|--------|---------|
| Operation ID | `remove_watch_v1_users__user_id__watchlist_remove_post` |
| Method | `POST` |
| Path | `/v1/users/{user_id}/watchlist/remove` |
| Parameters | `user_id` (path, Required) |
| Request Body | `[WatchlistRemoveRequest](#watchlistremoverequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## GET /v1/users/{user_id}/watchlist/stats
**Get Watch Counts**

Get user's watchlist statistics.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_watch_counts_v1_users__user_id__watchlist_stats_get` |
| Method | `GET` |
| Path | `/v1/users/{user_id}/watchlist/stats` |
| Parameters | `user_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## Notifications

### GET /v1/users/{user_id}/watchlist/notifications
**Get Notifications**

Get user's recent watchlist notifications.

| Aspect | Details |
|--------|---------|
| Operation ID | `get_notifications_v1_users__user_id__watchlist_notifications_get` |
| Method | `GET` |
| Path | `/v1/users/{user_id}/watchlist/notifications` |
| Parameters | `user_id` (path, Required) `hours` (query, Optional) `limit` (query, Optional) `offset` (query, Optional) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

### PUT /v1/users/{user_id}/watchlist/notifications/{notification_id}/check
**Mark Checked**

Mark a notification as checked.

| Aspect | Details |
|--------|---------|
| Operation ID | `mark_checked_v1_users__user_id__watchlist_notifications__notification_id__check_put` |
| Method | `PUT` |
| Path | `/v1/users/{user_id}/watchlist/notifications/{notification_id}/check` |
| Parameters | `user_id` (path, Required) `notification_id` (path, Required) |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## Related Links

- [← Back to API](../API.md)
- [Users API](./USERS.md)