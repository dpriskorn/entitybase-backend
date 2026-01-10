# REST API Endpoints

| Implemented | Method | Full Path | Description |
|-------------|--------|-----------|-------------|
| ✅ | GET | `/entitybase/v1/entities` | List entities, optionally filtered by type (or all entities if no type specified). |
| ✅ | POST | `/entitybase/v1/entities/items` | Create a new item entity. |
| ✅ | POST | `/entitybase/v1/entities/lexemes` | Create a new lexeme entity. |
| ✅ | POST | `/entitybase/v1/entities/properties` | Create a new property entity. |
| ✅ | GET | `/entitybase/v1/entities/{entity_id}` | Retrieve a single entity by its ID. |
| ✅ | GET | `/entitybase/v1/entities/{entity_id}/history` | Get the revision history for an entity. |
| ✅ | GET | `/entitybase/v1/entities/{entity_id}/revision/{revision_id}` | Get a specific revision of an entity. |
| ✅ | GET | `/entitybase/v1/health` | Health check endpoint that redirects or provides status. |
| ✅ | PUT | `/entitybase/v1/item/{entity_id}` | Update an existing item entity. |
| ✅ | POST | `/entitybase/v1/json-import` | Import entities from Wikidata JSONL dump file. |
| ✅ | PUT | `/entitybase/v1/lexeme/{entity_id}` | Update an existing lexeme entity. |
| ✅ | PUT | `/entitybase/v1/property/{entity_id}` | Update an existing property entity. |
| ✅ | POST | `/entitybase/v1/statements/batch` | Retrieve multiple statements by their content hashes in a batch request. |
| ✅ | POST | `/entitybase/v1/statements/cleanup-orphaned` | Clean up orphaned statements that are no longer referenced. |
| ✅ | GET | `/entitybase/v1/statements/most_used` | Get the most used statements based on reference count. |
| ✅ | GET | `/entitybase/v1/statements/{content_hash}` | Retrieve a single statement by its content hash. |
| ❌ | GET | `/wikibase/v1/entities` | Search entities - stub |
| ❌ | POST | `/wikibase/v1/entities/items` | Create item - redirects to entitybase endpoint |
| ❌ | GET | `/wikibase/v1/entities/items/{item_id}` | Get item |
| ❌ | PUT | `/wikibase/v1/entities/items/{item_id}` | Update item - stub |
| ❌ | GET | `/wikibase/v1/entities/items/{item_id}/aliases` | Get item aliases - stub |
| ❌ | GET | `/wikibase/v1/entities/items/{item_id}/aliases/{language_code}` | Get item aliases for language - stub |
| ❌ | PUT | `/wikibase/v1/entities/items/{item_id}/aliases/{language_code}` | Set item aliases for language - stub |
| ❌ | DELETE | `/wikibase/v1/entities/items/{item_id}/aliases/{language_code}` | Delete item aliases for language - stub |
| ❌ | GET | `/wikibase/v1/entities/items/{item_id}/descriptions` | Get item descriptions - stub |
| ❌ | GET | `/wikibase/v1/entities/items/{item_id}/descriptions/{language_code}` | Get item description for language - stub |
| ❌ | PUT | `/wikibase/v1/entities/items/{item_id}/descriptions/{language_code}` | Set item description for language - stub |
| ❌ | DELETE | `/wikibase/v1/entities/items/{item_id}/descriptions/{language_code}` | Delete item description for language - stub |
| ❌ | GET | `/wikibase/v1/entities/items/{item_id}/labels` | Get item labels - stub |
| ❌ | GET | `/wikibase/v1/entities/items/{item_id}/labels/{language_code}` | Get item label for language - stub |
| ❌ | PUT | `/wikibase/v1/entities/items/{item_id}/labels/{language_code}` | Set item label for language - stub |
| ❌ | DELETE | `/wikibase/v1/entities/items/{item_id}/labels/{language_code}` | Delete item label for language - stub |
| ❌ | GET | `/wikibase/v1/entities/items/{item_id}/labels_with_language_fallback/{language_code}` | Get item labels with language fallback - stub |
| ❌ | GET | `/wikibase/v1/entities/items/{item_id}/properties` | Get item properties - stub |
| ❌ | POST | `/wikibase/v1/entities/items/{item_id}/properties` | Add item property - stub |
| ❌ | GET | `/wikibase/v1/entities/items/{item_id}/sitelinks` | Get item sitelinks - stub |
| ❌ | POST | `/wikibase/v1/entities/lexemes` | Create lexeme - redirects to entitybase endpoint |
| ❌ | GET | `/wikibase/v1/entities/lexemes/{lexeme_id}` | Get lexeme |
| ❌ | PUT | `/wikibase/v1/entities/lexemes/{lexeme_id}` | Update lexeme - stub |
| ❌ | POST | `/wikibase/v1/entities/properties` | Create property - redirects to entitybase endpoint |
| ❌ | GET | `/wikibase/v1/entities/properties/{property_id}` | Get property |
| ❌ | PUT | `/wikibase/v1/entities/properties/{property_id}` | Update property - stub |
| ❌ | GET | `/wikibase/v1/entities/properties/{property_id}/aliases` | Get property aliases - stub |
| ❌ | GET | `/wikibase/v1/entities/properties/{property_id}/aliases/{language_code}` | Get property aliases for language - stub |
| ❌ | PUT | `/wikibase/v1/entities/properties/{property_id}/aliases/{language_code}` | Set property aliases for language - stub |
| ❌ | DELETE | `/wikibase/v1/entities/properties/{property_id}/aliases/{language_code}` | Delete property aliases for language - stub |
| ❌ | GET | `/wikibase/v1/entities/properties/{property_id}/descriptions` | Get property descriptions - stub |
| ❌ | GET | `/wikibase/v1/entities/properties/{property_id}/descriptions/{language_code}` | Get property description for language - stub |
| ❌ | PUT | `/wikibase/v1/entities/properties/{property_id}/descriptions/{language_code}` | Set property description for language - stub |
| ❌ | DELETE | `/wikibase/v1/entities/properties/{property_id}/descriptions/{language_code}` | Delete property description for language - stub |
| ❌ | GET | `/wikibase/v1/entities/properties/{property_id}/labels` | Get property labels - stub |
| ❌ | GET | `/wikibase/v1/entities/properties/{property_id}/labels/{language_code}` | Get property label for language - stub |
| ❌ | PUT | `/wikibase/v1/entities/properties/{property_id}/labels/{language_code}` | Set property label for language - stub |
| ❌ | DELETE | `/wikibase/v1/entities/properties/{property_id}/labels/{language_code}` | Delete property label for language - stub |
| ❌ | GET | `/wikibase/v1/entities/properties/{property_id}/labels_with_language_fallback/{language_code}` | Get property labels with language fallback - stub |
| ❌ | GET | `/wikibase/v1/entities/properties/{property_id}/properties` | Get property properties - stub |
| ❌ | GET | `/wikibase/v1/entities/properties/{property_id}/sitelinks` | Get property sitelinks - stub |
| ❌ | GET | `/wikibase/v1/statements` | Get statements - stub |

| Status | Count |
|--------|-------|
| Implemented | 16 |
| Not Implemented | 42 |
| Total | 58 |
