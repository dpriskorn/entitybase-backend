# REST API Endpoints

| Implemented | Method | Full Path | File |
|-------------|--------|-----------|------|
| ❌ | GET | `/entitybase/v1/entities` | src/models/rest_api/entitybase/v1/entities.py |
| ✅ | GET | `/entitybase/v1/entities/{entity_id}` | src/models/rest_api/entitybase/v1/entities.py |
| ✅ | GET | `/entitybase/v1/entities/{entity_id}/history` | src/models/rest_api/entitybase/v1/entities.py |
| ✅ | GET | `/entitybase/v1/entities/{entity_id}/revision/{revision_id}` | src/models/rest_api/entitybase/v1/entities.py |
| ✅ | GET | `/entitybase/v1/health` | src/models/rest_api/entitybase/v1/health.py |
| ✅ | POST | `/entitybase/v1/entities/items` | src/models/rest_api/entitybase/v1/items.py |
| ✅ | PUT | `/entitybase/v1/item/{entity_id}` | src/models/rest_api/entitybase/v1/items.py |
| ✅ | PUT | `/entitybase/v1/lexeme/{entity_id}` | src/models/rest_api/entitybase/v1/items.py |
| ✅ | PUT | `/entitybase/v1/property/{entity_id}` | src/models/rest_api/entitybase/v1/items.py |
| ✅ | POST | `/entitybase/v1/entities/lexemes` | src/models/rest_api/entitybase/v1/lexemes.py |
| ✅ | GET | `/entitybase/v1/statement/most_used` | src/models/rest_api/entitybase/v1/statements.py |
| ❌ | GET | `/wikibase/v1/entities` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | POST | `/wikibase/v1/entities/items` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | GET | `/wikibase/v1/entities/items/{item_id}` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | PUT | `/wikibase/v1/entities/items/{item_id}` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | GET | `/wikibase/v1/entities/items/{item_id}/aliases` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | GET | `/wikibase/v1/entities/items/{item_id}/aliases/{language_code}` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | PUT | `/wikibase/v1/entities/items/{item_id}/aliases/{language_code}` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | DELETE | `/wikibase/v1/entities/items/{item_id}/aliases/{language_code}` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | GET | `/wikibase/v1/entities/items/{item_id}/descriptions` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | GET | `/wikibase/v1/entities/items/{item_id}/descriptions/{language_code}` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | PUT | `/wikibase/v1/entities/items/{item_id}/descriptions/{language_code}` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | DELETE | `/wikibase/v1/entities/items/{item_id}/descriptions/{language_code}` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | GET | `/wikibase/v1/entities/items/{item_id}/labels` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | GET | `/wikibase/v1/entities/items/{item_id}/labels/{language_code}` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | PUT | `/wikibase/v1/entities/items/{item_id}/labels/{language_code}` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | DELETE | `/wikibase/v1/entities/items/{item_id}/labels/{language_code}` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | GET | `/wikibase/v1/entities/items/{item_id}/labels_with_language_fallback/{language_code}` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | GET | `/wikibase/v1/entities/items/{item_id}/properties` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | POST | `/wikibase/v1/entities/items/{item_id}/properties` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | GET | `/wikibase/v1/entities/items/{item_id}/sitelinks` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | POST | `/wikibase/v1/entities/properties` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | GET | `/wikibase/v1/entities/properties/{property_id}` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | PUT | `/wikibase/v1/entities/properties/{property_id}` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | GET | `/wikibase/v1/entities/properties/{property_id}/aliases` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | GET | `/wikibase/v1/entities/properties/{property_id}/aliases/{language_code}` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | PUT | `/wikibase/v1/entities/properties/{property_id}/aliases/{language_code}` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | DELETE | `/wikibase/v1/entities/properties/{property_id}/aliases/{language_code}` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | GET | `/wikibase/v1/entities/properties/{property_id}/descriptions` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | GET | `/wikibase/v1/entities/properties/{property_id}/descriptions/{language_code}` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | PUT | `/wikibase/v1/entities/properties/{property_id}/descriptions/{language_code}` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | DELETE | `/wikibase/v1/entities/properties/{property_id}/descriptions/{language_code}` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | GET | `/wikibase/v1/entities/properties/{property_id}/labels` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | GET | `/wikibase/v1/entities/properties/{property_id}/labels/{language_code}` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | PUT | `/wikibase/v1/entities/properties/{property_id}/labels/{language_code}` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | DELETE | `/wikibase/v1/entities/properties/{property_id}/labels/{language_code}` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | GET | `/wikibase/v1/entities/properties/{property_id}/labels_with_language_fallback/{language_code}` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | GET | `/wikibase/v1/entities/properties/{property_id}/properties` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | GET | `/wikibase/v1/entities/properties/{property_id}/sitelinks` | src/models/rest_api/wikibase/v1/entities.py |
| ❌ | GET | `/wikibase/v1/statements` | src/models/rest_api/wikibase/v1/entities.py |

| Status | Count |
|--------|-------|
| Implemented | 10 |
| Not Implemented | 40 |
| Total | 50 |
