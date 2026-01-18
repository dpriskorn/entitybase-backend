# REST API Endpoints

| Implemented | Method | Full Path | Description |
|-------------|--------|-----------|-------------|
| ✅ | GET | `/entitybase/v1/aliases/{hashes}` | Get batch aliases by hashes. |
| ✅ | GET | `/entitybase/v1/descriptions/{hashes}` | Get batch descriptions by hashes. |
| ✅ | GET | `/entitybase/v1/entities` | List entities based on type, limit, and offset. |
| ✅ | POST | `/entitybase/v1/entities/{entity_id}/revert-redirect` | No description |
| ✅ | GET | `/entitybase/v1/entity/{entity_id}/properties/{property_list}` | Get statement hashes for specified properties in an entity. |
| ✅ | POST | `/entitybase/v1/entitybase/v1/entities/{entity_id}/revert` | Revert entity to a previous revision. |
| ✅ | POST | `/entitybase/v1/entitybase/v1/entities/{entity_id}/revisions/{revision_id}/thank` | Send a thank for a specific revision. |
| ✅ | GET | `/entitybase/v1/entitybase/v1/entities/{entity_id}/revisions/{revision_id}/thanks` | Get all thanks for a specific revision. |
| ✅ | POST | `/entitybase/v1/entitybase/v1/statements/{statement_hash}/endorse` | Endorse a statement to signal trust. |
| ✅ | DELETE | `/entitybase/v1/entitybase/v1/statements/{statement_hash}/endorse` | Withdraw endorsement from a statement. |
| ✅ | GET | `/entitybase/v1/entitybase/v1/statements/{statement_hash}/endorsements` | Get endorsements for a statement. |
| ✅ | GET | `/entitybase/v1/entitybase/v1/statements/{statement_hash}/endorsements/stats` | Get endorsement statistics for a statement. |
| ✅ | GET | `/entitybase/v1/entitybase/v1/users/{user_id}/endorsements` | Get endorsements given by a user. |
| ✅ | GET | `/entitybase/v1/entitybase/v1/users/{user_id}/endorsements/stats` | Get endorsement statistics for a user. |
| ✅ | GET | `/entitybase/v1/entitybase/v1/users/{user_id}/thanks/received` | Get thanks received by user. |
| ✅ | GET | `/entitybase/v1/entitybase/v1/users/{user_id}/thanks/sent` | Get thanks sent by user. |
| ✅ | GET | `/entitybase/v1/health` | Health check endpoint for monitoring service status. |
| ✅ | GET | `/entitybase/v1/labels/{hashes}` | Get batch labels by hashes. |
| ✅ | GET | `/entitybase/v1/qualifiers/{hashes}` | Fetch qualifiers by hash(es). |
| ✅ | POST | `/entitybase/v1/redirects` | No description |
| ✅ | GET | `/entitybase/v1/references/{hashes}` | Fetch references by hash(es). |
| ✅ | GET | `/entitybase/v1/sitelinks/{hashes}` | Get batch sitelink titles by hashes. |
| ✅ | GET | `/entitybase/v1/statements/batch` | Get batch statements for entities and properties. |
| ✅ | GET | `/entitybase/v1/v1/health` | Redirect legacy /v1/health endpoint to /health. |
| ✅ | POST | `/entitybase/v1/v1/users` | Create a new user. |
| ✅ | GET | `/entitybase/v1/v1/users/{user_id}` | Get user information by MediaWiki user ID. |
| ✅ | PUT | `/entitybase/v1/v1/users/{user_id}/watchlist/toggle` | Enable or disable watchlist for user. |

| Status | Count |
|--------|-------|
| Implemented | 27 |
| Not Implemented | 0 |
| Total | 27 |
