# REST API Endpoints

| Implemented | Method | Full Path | Description |
|-------------|--------|-----------|-------------|
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
| ✅ | GET | `/entitybase/v1/entities/lexemes/{lexeme_id}/aliases/{language_code}` | Get lexeme aliases for language. |
| ✅ | PATCH | `/entitybase/v1/entities/lexemes/{lexeme_id}/aliases/{language_code}` | Patch lexeme aliases for language using JSON Patch. |
| ✅ | GET | `/entitybase/v1/entities/lexemes/{lexeme_id}/descriptions/{language_code}` | Get lexeme description for language. |
| ✅ | GET | `/entitybase/v1/entities/lexemes/{lexeme_id}/labels/{language_code}` | Get lexeme label for language. |
| ✅ | POST | `/entitybase/v1/entities/properties` | Create a new property entity. |
| ✅ | GET | `/entitybase/v1/entities/properties/{property_id}/aliases/{language_code}` | Get property aliases for language. |
| ✅ | PATCH | `/entitybase/v1/entities/properties/{property_id}/aliases/{language_code}` | Patch property aliases for language using JSON Patch. |
| ✅ | GET | `/entitybase/v1/entities/properties/{property_id}/descriptions/{language_code}` | Get property description for language. |
| ✅ | GET | `/entitybase/v1/entities/properties/{property_id}/labels/{language_code}` | Get property label for language. |
| ✅ | GET | `/entitybase/v1/entities/{entity_id}` | Retrieve a single entity by its ID. |
| ✅ | DELETE | `/entitybase/v1/entities/{entity_id}` | No description |
| ✅ | GET | `/entitybase/v1/entities/{entity_id}.ttl` | No description |
| ✅ | GET | `/entitybase/v1/entities/{entity_id}/history` | Get the revision history for an entity. |
| ✅ | GET | `/entitybase/v1/entities/{entity_id}/properties` | No description |
| ✅ | GET | `/entitybase/v1/entities/{entity_id}/properties/{property_list}` | No description |
| ✅ | GET | `/entitybase/v1/entities/{entity_id}/revision/{revision_id}` | Get a specific revision of an entity. |
| ✅ | GET | `/entitybase/v1/entities/{entity_id}/revision/{revision_id}/json` | Get JSON representation of a specific entity revision. |
| ✅ | GET | `/entitybase/v1/entities/{entity_id}/revision/{revision_id}/rdf` | Get RDF representation of a specific entity revision. |
| ✅ | GET | `/entitybase/v1/entities/{entity_id}/revisions/raw/{revision_id}` | No description |
| ✅ | GET | `/entitybase/v1/health` | Health check endpoint that redirects or provides status. |
| ✅ | PUT | `/entitybase/v1/item/{entity_id}` | Update an existing item entity. |
| ✅ | POST | `/entitybase/v1/json-import` | Import entities from Wikidata JSONL dump file. |
| ✅ | PUT | `/entitybase/v1/lexeme/{entity_id}` | Update an existing lexeme entity. |
| ✅ | PUT | `/entitybase/v1/property/{entity_id}` | Update an existing property entity. |
| ✅ | POST | `/entitybase/v1/statements/batch` | Retrieve multiple statements by their content hashes in a batch request. |
| ✅ | POST | `/entitybase/v1/statements/cleanup-orphaned` | Clean up orphaned statements that are no longer referenced. |
| ✅ | GET | `/entitybase/v1/statements/most_used` | Get the most used statements based on reference count. |
| ✅ | GET | `/entitybase/v1/statements/{content_hash}` | Retrieve a single statement by its content hash. |

| Status | Count |
|--------|-------|
| Implemented | 39 |
| Not Implemented | 0 |
| Total | 39 |
