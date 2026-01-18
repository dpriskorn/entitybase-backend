# REST API Endpoints

| Implemented | Method | Full Path | Description |
|-------------|--------|-----------|-------------|
| ✅ | POST | `/entitybase/entitybase/v1/users` | Create a new user. |
| ✅ | GET | `/entitybase/entitybase/v1/users/stat` | Get user statistics. |
| ✅ | GET | `/entitybase/entitybase/v1/users/{user_id}` | Get user information by MediaWiki user ID. |
| ✅ | GET | `/entitybase/v1/entities` | List entities based on type, limit, and offset. |
| ✅ | GET | `/entitybase/v1/entities/aliases/{hashes}` | Get batch aliases by hashes. |
| ✅ | GET | `/entitybase/v1/entities/descriptions/{hashes}` | Get batch descriptions by hashes. |
| ✅ | POST | `/entitybase/v1/entities/items` | Create a new item entity. |
| ✅ | GET | `/entitybase/v1/entities/items/{item_id}/aliases/{language_code}` | Get item aliases for language. |
| ✅ | PUT | `/entitybase/v1/entities/items/{item_id}/aliases/{language_code}` | Update item aliases for language. |
| ✅ | GET | `/entitybase/v1/entities/items/{item_id}/descriptions/{language_code}` | Get item description for language. |
| ✅ | PUT | `/entitybase/v1/entities/items/{item_id}/descriptions/{language_code}` | Update item description for language. |
| ✅ | DELETE | `/entitybase/v1/entities/items/{item_id}/descriptions/{language_code}` | Delete item description for language. |
| ✅ | GET | `/entitybase/v1/entities/items/{item_id}/labels/{language_code}` | Get item label for language. |
| ✅ | PUT | `/entitybase/v1/entities/items/{item_id}/labels/{language_code}` | Update item label for language. |
| ✅ | DELETE | `/entitybase/v1/entities/items/{item_id}/labels/{language_code}` | Delete item label for language. |
| ✅ | GET | `/entitybase/v1/entities/labels/{hashes}` | Get batch labels by hashes. |
| ✅ | POST | `/entitybase/v1/entities/lexemes` | Create a new lexeme entity. |
| ✅ | POST | `/entitybase/v1/entities/properties` | Create a new property entity. |
| ✅ | GET | `/entitybase/v1/entities/properties/{property_id}/aliases/{language_code}` | Get property aliases for language. |
| ✅ | PUT | `/entitybase/v1/entities/properties/{property_id}/aliases/{language_code}` | Update property aliases for language. |
| ✅ | GET | `/entitybase/v1/entities/properties/{property_id}/descriptions/{language_code}` | Get property description for language. |
| ✅ | GET | `/entitybase/v1/entities/properties/{property_id}/labels/{language_code}` | Get property label for language. |
| ✅ | GET | `/entitybase/v1/entities/sitelinks/{hashes}` | Get batch sitelink titles by hashes. |
| ✅ | GET | `/entitybase/v1/entities/{entity_id}` | Retrieve a single entity by its ID. |
| ✅ | DELETE | `/entitybase/v1/entities/{entity_id}` | Delete an entity. |
| ✅ | GET | `/entitybase/v1/entities/{entity_id}.json` | Get entity data in JSON format. |
| ✅ | GET | `/entitybase/v1/entities/{entity_id}.ttl` | Get entity data in Turtle format. |
| ✅ | GET | `/entitybase/v1/entities/{entity_id}/history` | Get the revision history for an entity. |
| ✅ | GET | `/entitybase/v1/entities/{entity_id}/properties` | Get entity property hashes for specified properties. |
| ✅ | POST | `/entitybase/v1/entities/{entity_id}/properties/{property_id}` | Add claims for a single property to an entity. |
| ✅ | GET | `/entitybase/v1/entities/{entity_id}/properties/{property_list}` | Get entity property hashes for specified properties. |
| ✅ | PUT | `/entitybase/v1/entities/{entity_id}/sitelinks` | Update entity sitelinks. |
| ✅ | POST | `/entitybase/v1/entities/{entity_id}/revert` | Revert entity to a previous revision. |
| ✅ | POST | `/entitybase/v1/entities/{entity_id}/revert-redirect` | No description |
| ✅ | GET | `/entitybase/v1/entities/{entity_id}/revision/{revision_id}` | Get a specific revision of an entity. |
| ✅ | GET | `/entitybase/v1/entities/{entity_id}/revision/{revision_id}/json` | Get JSON representation of a specific entity revision. |
| ✅ | GET | `/entitybase/v1/entities/{entity_id}/revision/{revision_id}/ttl` | Get Turtle (TTL) representation of a specific entity revision. |
| ✅ | POST | `/entitybase/v1/entities/{entity_id}/revisions/{revision_id}/thank` | Send a thank for a specific revision. |
| ✅ | GET | `/entitybase/v1/entities/{entity_id}/revisions/{revision_id}/thanks` | Get all thanks for a specific revision. |
| ✅ | DELETE | `/entitybase/v1/entities/{entity_id}/statements/{statement_hash}` | Remove a statement by hash from an entity. |
| ✅ | PATCH | `/entitybase/v1/entities/{entity_id}/statements/{statement_hash}` | Replace a statement by hash with new claim data. |
| ✅ | GET | `/entitybase/v1/entity/{entity_id}/properties/{property_list}` | Get statement hashes for specified properties in an entity. |
| ✅ | POST | `/entitybase/v1/json-import` | Import entities from Wikidata JSONL dump file. |
| ✅ | GET | `/entitybase/v1/qualifiers/{hashes}` | Fetch qualifiers by hash(es). |
| ✅ | POST | `/entitybase/v1/redirects` | Create a redirect for an entity. |
| ✅ | GET | `/entitybase/v1/references/{hashes}` | Fetch references by hash(es). |
| ✅ | GET | `/entitybase/v1/statements/batch` | Get batch statements for entities and properties. |
| ✅ | POST | `/entitybase/v1/statements/batch` | Retrieve multiple statements by their content hashes in a batch request. |
| ✅ | POST | `/entitybase/v1/statements/cleanup-orphaned` | Clean up orphaned statements that are no longer referenced. |
| ✅ | GET | `/entitybase/v1/statements/most_used` | Get the most used statements based on reference count. |
| ✅ | GET | `/entitybase/v1/statements/{content_hash}` | Retrieve a single statement by its content hash. |
| ✅ | POST | `/entitybase/v1/statements/{statement_hash}/endorse` | Endorse a statement to signal trust. |
| ✅ | DELETE | `/entitybase/v1/statements/{statement_hash}/endorse` | Withdraw endorsement from a statement. |
| ✅ | GET | `/entitybase/v1/statements/{statement_hash}/endorsements` | Get endorsements for a statement. |
| ✅ | GET | `/entitybase/v1/statements/{statement_hash}/endorsements/stats` | Get endorsement statistics for a statement. |
| ✅ | GET | `/entitybase/v1/stats` | Get general wiki statistics. |
| ✅ | GET | `/entitybase/v1/users/{user_id}/endorsements` | Get endorsements given by a user. |
| ✅ | GET | `/entitybase/v1/users/{user_id}/endorsements/stats` | Get endorsement statistics for a user. |
| ✅ | GET | `/entitybase/v1/users/{user_id}/thanks/received` | Get thanks received by user. |
| ✅ | GET | `/entitybase/v1/users/{user_id}/thanks/sent` | Get thanks sent by user. |
| ✅ | POST | `/entitybase/v1/users/{user_id}/watchlist` | Add a watchlist entry for user. |
| ✅ | GET | `/entitybase/v1/users/{user_id}/watchlist` | Get user's watchlist. |
| ✅ | GET | `/entitybase/v1/users/{user_id}/watchlist/notifications` | Get user's recent watchlist notifications. |
| ✅ | PUT | `/entitybase/v1/users/{user_id}/watchlist/notifications/{notification_id}/check` | Mark a notification as checked. |
| ✅ | POST | `/entitybase/v1/users/{user_id}/watchlist/remove` | Remove a watchlist entry for user. |
| ✅ | GET | `/entitybase/v1/users/{user_id}/watchlist/stats` | Get user's watchlist statistics. |
| ✅ | PUT | `/entitybase/v1/users/{user_id}/watchlist/toggle` | Enable or disable watchlist for user. |
| ✅ | DELETE | `/entitybase/v1/users/{user_id}/watchlist/{watch_id}` | Remove a watchlist entry by ID. |
| ✅ | GET | `/health` | Health check endpoint for monitoring service status. |

| Status | Count |
|--------|-------|
| Implemented | 70 |
| Not Implemented | 0 |
| Total | 70 |
