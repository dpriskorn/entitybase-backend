# Next Steps Plan for Subgraph Protection System

## Immediate Next Steps (High Priority)

### 1. Implement Remaining Entity Operations
Add logging for `entity_create`, `entity_edit`, `entity_delete`, `entity_undelete`, `entity_lock`, `entity_unlock`, `entity_archive`, `entity_unarchive` operations.

- **entity_create**: Log in `EntityCreateHandler.create_entity()` after successful creation
- **entity_edit**: Log in `EntityUpdateHandler.update_entity()` after successful update
- **entity_delete**: Log in `EntityDeleteHandler.delete_entity()` after successful deletion
- **entity_undelete**: Log when undeleting entities (if implemented)
- **entity_lock/unlock**: Log when changing lock status
- **entity_archive/unarchive**: Log when changing archive status

**Implementation Details:**
- Extract user_id from `request.editor` field (placeholder method needed)
- Log activity with `vitess_client.user_repository.log_user_activity()`
- Include entity_id and revision_id in log
- Handle cases where editor/user info is missing

**Files to Modify:**
- `src/models/rest_api/handlers/entity/create.py`
- `src/models/rest_api/handlers/entity/update.py`
- `src/models/rest_api/handlers/entity/delete.py`
- Any lock/archive handlers

**Testing:**
- Unit tests for activity logging in each handler
- Integration tests verifying activities appear in user activity endpoint

**Effort:** 2-3 days

### 2. Auto-Disable Background Worker
Implement `WatchlistAutoDisableWorker` to automatically disable watchlists for users inactive >30 days.

- **Worker Logic:**
  - Query users with `last_activity < NOW() - 30 days`
  - Set `watchlist_enabled = FALSE`
  - Optional: Clear existing watches/notifications
  - Send notification before disabling (if possible)

- **Scheduling:** Daily cron job or Kubernetes CronJob
- **Configuration:** Make inactivity threshold configurable
- **Logging:** Track disabled users and cleanup stats

**Files to Create:**
- `src/models/workers/watchlist_auto_disable/main.py`

**Integration:**
- Update user activity tracking in watchlist/watch interaction points
- Ensure activity timestamps are updated correctly

**Effort:** 1-2 days

## Medium Priority Enhancements

### 3. Notification Preferences
Add user-configurable notification settings.

- **Settings Fields:** notification_limit (50/100/250/500), retention_hours (24/72/168/720)
- **API:** GET/PUT `/v1/users/{user_id}/settings`
- **Override:** Allow frontend to specify custom limits per request
- **Storage:** Extend users table with preferences JSON

**Effort:** 1-2 days

### 4. Bulk Operations
Support bulk watchlist and notification operations.

- **Bulk Add/Remove:** Accept arrays of entities in watchlist API
- **Bulk Notifications:** Mark multiple as checked
- **Limits:** Reasonable caps (e.g., 100 entities per bulk operation)

**Effort:** 1-2 days

## Long-term Goals

### 5. Advanced Analytics
- Activity dashboards and contribution metrics
- Moderation tools for subgraph monitoring
- ML-based vandalism detection

### 6. Performance Optimizations
- Caching for watchlist queries
- Real-time notifications via WebSockets
- Horizontal scaling improvements

## Current Status
- ✅ User registration & watchlist management
- ✅ Notification system with cleanup
- ✅ Revert API with activity logging
- 🔄 In progress: Full entity operation logging
- ⏳ Next: Auto-disable worker

## Implementation Order
1. Complete entity operation logging (current)
2. Add auto-disable worker
3. User preferences
4. Bulk operations

Priority: Complete core functionality first, then enhancements.