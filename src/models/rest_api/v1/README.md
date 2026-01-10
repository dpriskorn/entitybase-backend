# REST API Endpoints

This document lists all available endpoints in the EntityBase REST API.

## Base URLs

- EntityBase API: `https://api.example.com/entitybase/v1`
- Wikibase Compatibility API: `https://api.example.com/wikibase/v1`

## EntityBase v1 Endpoints

| Method | Path | Full Path | Description |
|--------|------|-----------|-------------|
| GET | `/entities` | `/entitybase/v1/entities` | Search entities |
| GET | `/entities/{entity_id}` | `/entitybase/v1/entities/{entity_id}` | Get entity by ID |
| GET | `/entities/{entity_id}/history` | `/entitybase/v1/entities/{entity_id}/history` | Get entity revision history |
| GET | `/entities/{entity_id}/revision/{revision_id}` | `/entitybase/v1/entities/{entity_id}/revision/{revision_id}` | Get specific revision |
| GET | `/health` | `/entitybase/v1/health` | Health check |
| POST | `/entities/items` | `/entitybase/v1/entities/items` | Create new item |
| PUT | `/item/{entity_id}` | `/entitybase/v1/item/{entity_id}` | Update item |
| PUT | `/lexeme/{entity_id}` | `/entitybase/v1/lexeme/{entity_id}` | Update lexeme |
| PUT | `/property/{entity_id}` | `/entitybase/v1/property/{entity_id}` | Update property |
| POST | `/entities/lexemes` | `/entitybase/v1/entities/lexemes` | Create new lexeme |
| GET | `/statement/most_used` | `/entitybase/v1/statement/most_used` | Get most used statements |

## Wikibase v1 Compatibility Endpoints

| Method | Path | Full Path | Description |
|--------|------|-----------|-------------|
| GET | `/entities` | `/wikibase/v1/entities` | Search entities |
| POST | `/entities/items` | `/wikibase/v1/entities/items` | Create item |
| GET | `/entities/items/{item_id}` | `/wikibase/v1/entities/items/{item_id}` | Get item |
| PUT | `/entities/items/{item_id}` | `/wikibase/v1/entities/items/{item_id}` | Update item |
| GET | `/entities/items/{item_id}/aliases` | `/wikibase/v1/entities/items/{item_id}/aliases` | Get item aliases |
| GET | `/entities/items/{item_id}/aliases/{language_code}` | `/wikibase/v1/entities/items/{item_id}/aliases/{language_code}` | Get item aliases for language |
| PUT | `/entities/items/{item_id}/aliases/{language_code}` | `/wikibase/v1/entities/items/{item_id}/aliases/{language_code}` | Set item aliases for language |
| DELETE | `/entities/items/{item_id}/aliases/{language_code}` | `/wikibase/v1/entities/items/{item_id}/aliases/{language_code}` | Delete item aliases for language |
| GET | `/entities/items/{item_id}/descriptions` | `/wikibase/v1/entities/items/{item_id}/descriptions` | Get item descriptions |
| GET | `/entities/items/{item_id}/descriptions/{language_code}` | `/wikibase/v1/entities/items/{item_id}/descriptions/{language_code}` | Get item description for language |
| PUT | `/entities/items/{item_id}/descriptions/{language_code}` | `/wikibase/v1/entities/items/{item_id}/descriptions/{language_code}` | Set item description for language |
| DELETE | `/entities/items/{item_id}/descriptions/{language_code}` | `/wikibase/v1/entities/items/{item_id}/descriptions/{language_code}` | Delete item description for language |
| GET | `/entities/items/{item_id}/labels` | `/wikibase/v1/entities/items/{item_id}/labels` | Get item labels |
| GET | `/entities/items/{item_id}/labels/{language_code}` | `/wikibase/v1/entities/items/{item_id}/labels/{language_code}` | Get item label for language |
| PUT | `/entities/items/{item_id}/labels/{language_code}` | `/wikibase/v1/entities/items/{item_id}/labels/{language_code}` | Set item label for language |
| DELETE | `/entities/items/{item_id}/labels/{language_code}` | `/wikibase/v1/entities/items/{item_id}/labels/{language_code}` | Delete item label for language |
| GET | `/entities/items/{item_id}/labels_with_language_fallback/{language_code}` | `/wikibase/v1/entities/items/{item_id}/labels_with_language_fallback/{language_code}` | Get item labels with fallback |
| GET | `/entities/items/{item_id}/properties` | `/wikibase/v1/entities/items/{item_id}/properties` | Get item properties |
| POST | `/entities/items/{item_id}/properties` | `/wikibase/v1/entities/items/{item_id}/properties` | Add item property |
| GET | `/entities/items/{item_id}/sitelinks` | `/wikibase/v1/entities/items/{item_id}/sitelinks` | Get item sitelinks |
| POST | `/entities/properties` | `/wikibase/v1/entities/properties` | Create property |
| GET | `/entities/properties/{property_id}` | `/wikibase/v1/entities/properties/{property_id}` | Get property |
| PUT | `/entities/properties/{property_id}` | `/wikibase/v1/entities/properties/{property_id}` | Update property |
| GET | `/entities/properties/{property_id}/aliases` | `/wikibase/v1/entities/properties/{property_id}/aliases` | Get property aliases |
| GET | `/entities/properties/{property_id}/aliases/{language_code}` | `/wikibase/v1/entities/properties/{property_id}/aliases/{language_code}` | Get property aliases for language |
| PUT | `/entities/properties/{property_id}/aliases/{language_code}` | `/wikibase/v1/entities/properties/{property_id}/aliases/{language_code}` | Set property aliases for language |
| DELETE | `/entities/properties/{property_id}/aliases/{language_code}` | `/wikibase/v1/entities/properties/{property_id}/aliases/{language_code}` | Delete property aliases for language |
| GET | `/entities/properties/{property_id}/descriptions` | `/wikibase/v1/entities/properties/{property_id}/descriptions` | Get property descriptions |
| GET | `/entities/properties/{property_id}/descriptions/{language_code}` | `/wikibase/v1/entities/properties/{property_id}/descriptions/{language_code}` | Get property description for language |
| PUT | `/entities/properties/{property_id}/descriptions/{language_code}` | `/wikibase/v1/entities/properties/{property_id}/descriptions/{language_code}` | Set property description for language |
| DELETE | `/entities/properties/{property_id}/descriptions/{language_code}` | `/wikibase/v1/entities/properties/{property_id}/descriptions/{language_code}` | Delete property description for language |
| GET | `/entities/properties/{property_id}/labels` | `/wikibase/v1/entities/properties/{property_id}/labels` | Get property labels |
| GET | `/entities/properties/{property_id}/labels/{language_code}` | `/wikibase/v1/entities/properties/{property_id}/labels/{language_code}` | Get property label for language |
| PUT | `/entities/properties/{property_id}/labels/{language_code}` | `/wikibase/v1/entities/properties/{property_id}/labels/{language_code}` | Set property label for language |
| DELETE | `/entities/properties/{property_id}/labels/{language_code}` | `/wikibase/v1/entities/properties/{property_id}/labels/{language_code}` | Delete property label for language |
| GET | `/entities/properties/{property_id}/labels_with_language_fallback/{language_code}` | `/wikibase/v1/entities/properties/{property_id}/labels_with_language_fallback/{language_code}` | Get property labels with fallback |
| GET | `/entities/properties/{property_id}/properties` | `/wikibase/v1/entities/properties/{property_id}/properties` | Get property properties |
| GET | `/entities/properties/{property_id}/sitelinks` | `/wikibase/v1/entities/properties/{property_id}/sitelinks` | Get property sitelinks |
| GET | `/statements` | `/wikibase/v1/statements` | Get statements |

## Notes

- Wikibase compatibility endpoints are currently stubbed and return 501 Not Implemented
- EntityBase endpoints are functional for basic CRUD operations
- All endpoints require proper authentication and authorization
- Response formats follow EntityBase JSON Entity v1 schema