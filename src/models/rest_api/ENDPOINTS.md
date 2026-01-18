# REST API Endpoints

| Implemented | Method | Full Path | Description |
|-------------|--------|-----------|-------------|
| ✅ | GET | `/entitybase/v1/aliases/{hashes}` | Get batch aliases by hashes. |
| ✅ | GET | `/entitybase/v1/descriptions/{hashes}` | Get batch descriptions by hashes. |
| ✅ | GET | `/entitybase/v1/entities` | List entities based on type, limit, and offset. |
| ✅ | GET | `/entitybase/v1/entities` | List entities, optionally filtered by type (or all entities if no type specified). |
| ✅ | POST | `/entitybase/v1/entities/items` | Create a new item entity. |
| ✅ | GET | `/entitybase/v1/entities/items/{item_id}/aliases/{language_code}` | Get item aliases for language. |
| ✅ | PATCH | `/entitybase/v1/entities/items/{item_id}/aliases/{language_code}` | Patch item aliases for language using JSON Patch. |
| ✅ | GET | `/entitybase/v1/entities/items/{item_id}/descriptions/{language_code}` | Get item description for language. |
| ✅ | PUT | `/entitybase/v1/entities/items/{item_id}/descriptions/{language_code}` | Update item description for language. |
| ✅ | DELETE | `/entitybase/v1/entities/items/{item_id}/descriptions/{language_code}` | Delete item description for language. |
| ✅ | GET | `/entitybase/v1/entities/items/{item_id}/labels/{language_code}` | Get item label for language. |
| ✅ | PUT | `/entitybase/v1/entities/items/{item_id}/labels/{language_code}` | Update item label for language. |
| ✅ | DELETE | `/entitybase/v1/entities/items/{item_id}/labels/{language_code}` | Delete item label for language. |
| ✅ | POST | `/entitybase/v1/entities/lexemes` | Create a new lexeme entity. |
| ✅ | POST | `/entitybase/v1/entities/properties` | Create a new property entity. |
| ✅ | GET | `/entitybase/v1/entities/properties/{property_id}/aliases/{language_code}` | Get property aliases for language. |
| ✅ | PATCH | `/entitybase/v1/entities/properties/{property_id}/aliases/{language_code}` | Patch property aliases for language using JSON Patch. |
| ✅ | GET | `/entitybase/v1/entities/properties/{property_id}/descriptions/{language_code}` | Get property description for language. |
| ✅ | GET | `/entitybase/v1/entities/properties/{property_id}/labels/{language_code}` | Get property label for language. |
| ✅ | GET | `/entitybase/v1/entities/{entity_id}` | Retrieve a single entity by its ID. |
| ✅ | DELETE | `/entitybase/v1/entities/{entity_id}` | No description |
| ✅ | GET | `/entitybase/v1/entities/{entity_id}.ttl` | Get entity data in Turtle (RDF) format. |
| ✅ | GET | `/entitybase/v1/entities/{entity_id}/history` | Get the revision history for an entity. |
| ✅ | GET | `/entitybase/v1/entities/{entity_id}/properties` | No description |
| ✅ | GET | `/entitybase/v1/entities/{entity_id}/properties/{property_list}` | No description |
| ✅ | POST | `/entitybase/v1/entities/{entity_id}/revert-redirect` | No description |
| ✅ | GET | `/entitybase/v1/entities/{entity_id}/revision/{revision_id}` | Get a specific revision of an entity. |
| ✅ | GET | `/entitybase/v1/entities/{entity_id}/revision/{revision_id}/json` | Get JSON representation of a specific entity revision. |
| ✅ | GET | `/entitybase/v1/entities/{entity_id}/revision/{revision_id}/ttl` | Get TTL representation of a specific entity revision. |
| ✅ | GET | `/entitybase/v1/entities/{entity_id}/revisions/raw/{revision_id}` | No description |
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
| ✅ | GET | `/entitybase/v1/health` | Health check endpoint that redirects or provides status. |
| ✅ | PUT | `/entitybase/v1/item/{entity_id}` | Update an existing item entity. |
| ✅ | POST | `/entitybase/v1/json-import` | Import entities from Wikidata JSONL dump file. |
| ✅ | GET | `/entitybase/v1/labels/{hashes}` | Get batch labels by hashes. |
| ✅ | PUT | `/entitybase/v1/lexeme/{entity_id}` | Update an existing lexeme entity. |
| ✅ | PUT | `/entitybase/v1/property/{entity_id}` | Update an existing property entity. |
| ✅ | GET | `/entitybase/v1/qualifiers/{hashes}` | Fetch qualifiers by hash(es). |
| ✅ | POST | `/entitybase/v1/redirects` | No description |
| ✅ | GET | `/entitybase/v1/references/{hashes}` | Fetch references by hash(es). |
| ✅ | GET | `/entitybase/v1/sitelinks/{hashes}` | Get batch sitelink titles by hashes. |
| ✅ | GET | `/entitybase/v1/statements/batch` | Get batch statements for entities and properties. |
| ✅ | POST | `/entitybase/v1/statements/batch` | Retrieve multiple statements by their content hashes in a batch request. |
| ✅ | POST | `/entitybase/v1/statements/cleanup-orphaned` | Clean up orphaned statements that are no longer referenced. |
| ✅ | GET | `/entitybase/v1/statements/most_used` | Get the most used statements based on reference count. |
| ✅ | GET | `/entitybase/v1/statements/{content_hash}` | Retrieve a single statement by its content hash. |
| ✅ | GET | `/entitybase/v1/v1/health` | Redirect legacy /v1/health endpoint to /health. |
| ✅ | POST | `/entitybase/v1/v1/users` | Create a new user. |
| ✅ | GET | `/entitybase/v1/v1/users/{user_id}` | Get user information by MediaWiki user ID. |
| ✅ | PUT | `/entitybase/v1/v1/users/{user_id}/watchlist/toggle` | Enable or disable watchlist for user. |

| Status | Count |
|--------|-------|
| Implemented | 66 |
| Not Implemented | 0 |
| Total | 66 |
