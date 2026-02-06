# REST API Endpoints

| Implemented | Method | Full Path | Description |
|-------------|--------|-----------|-------------|
| ✅ | GET | `/entities` | List entities based on type, status, edit_type, limit, and offset. |
| ✅ | POST | `/entities/items` | Create a new item entity. |
| ✅ | GET | `/entities/items/{item_id}/aliases/{language_code}` | Get item aliases for language. |
| ✅ | PUT | `/entities/items/{item_id}/aliases/{language_code}` | Update item aliases for language. |
| ✅ | GET | `/entities/items/{item_id}/descriptions/{language_code}` | Get item description for language. |
| ✅ | PUT | `/entities/items/{item_id}/descriptions/{language_code}` | Update item description for language. |
| ✅ | DELETE | `/entities/items/{item_id}/descriptions/{language_code}` | Delete item description for language. |
| ✅ | GET | `/entities/items/{item_id}/labels/{language_code}` | Get item label for language. |
| ✅ | PUT | `/entities/items/{item_id}/labels/{language_code}` | Update item label for language. |
| ✅ | DELETE | `/entities/items/{item_id}/labels/{language_code}` | Delete item label for language. |
| ✅ | POST | `/entities/properties` | Create a new property entity. |
| ✅ | GET | `/entities/properties/{property_id}/aliases/{language_code}` | Get property aliases for language. |
| ✅ | PUT | `/entities/properties/{property_id}/aliases/{language_code}` | Update property aliases for language. |
| ✅ | GET | `/entities/properties/{property_id}/descriptions/{language_code}` | Get property description for language. |
| ✅ | GET | `/entities/properties/{property_id}/labels/{language_code}` | Get property label for language. |
| ✅ | GET | `/entities/{entity_id}` | Retrieve a single entity by its ID. |
| ✅ | DELETE | `/entities/{entity_id}` | Delete an entity. |
| ✅ | GET | `/entities/{entity_id}.json` | Get entity data in JSON format. |
| ✅ | GET | `/entities/{entity_id}.ttl` | Get entity data in Turtle format. |
| ✅ | GET | `/entities/{entity_id}/history` | Get the revision history for an entity. |
| ✅ | GET | `/entities/{entity_id}/properties` | Get list of unique property IDs for an entity's head revision. |
| ✅ | POST | `/entities/{entity_id}/properties/{property_id}` | Add claims for a single property to an entity. |
| ✅ | GET | `/entities/{entity_id}/properties/{property_list}` | Get entity property hashes for specified properties. |
| ✅ | POST | `/entities/{entity_id}/revert` | Revert entity to a previous revision. |
| ✅ | POST | `/entities/{entity_id}/revert-redirect` | No description |
| ✅ | GET | `/entities/{entity_id}/revision/{revision_id}` | Get a specific revision of an entity. |
| ✅ | GET | `/entities/{entity_id}/revision/{revision_id}/json` | Get JSON representation of a specific entity revision. |
| ✅ | GET | `/entities/{entity_id}/revision/{revision_id}/ttl` | Get Turtle (TTL) representation of a specific entity revision. |
| ✅ | POST | `/entities/{entity_id}/revisions/{revision_id}/thank` | Send a thank for a specific revision. |
| ✅ | GET | `/entities/{entity_id}/revisions/{revision_id}/thanks` | Get all thanks for a specific revision. |
| ✅ | GET | `/entities/{entity_id}/sitelinks/{site}` | Get a single sitelink for an entity. |
| ✅ | POST | `/entities/{entity_id}/sitelinks/{site}` | Add a new sitelink for an entity. |
| ✅ | PUT | `/entities/{entity_id}/sitelinks/{site}` | Update an existing sitelink for an entity. |
| ✅ | DELETE | `/entities/{entity_id}/sitelinks/{site}` | Delete a sitelink from an entity. |
| ✅ | DELETE | `/entities/{entity_id}/statements/{statement_hash}` | Remove a statement by hash from an entity. |
| ✅ | PATCH | `/entities/{entity_id}/statements/{statement_hash}` | Replace a statement by hash with new claim data. |
| ✅ | GET | `/entity/{entity_id}/properties/{property_list}` | Get statement hashes for specified properties in an entity. |
| ✅ | GET | `/entitybase/v1/entities/aliases/{hashes}` | Get batch aliases by hashes. |
| ✅ | GET | `/entitybase/v1/entities/descriptions/{hashes}` | Get batch descriptions by hashes. |
| ✅ | GET | `/entitybase/v1/entities/labels/{hashes}` | Get batch labels by hashes. |
| ✅ | GET | `/entitybase/v1/entities/sitelinks/{hashes}` | Get batch sitelink titles by hashes. |
| ✅ | GET | `/entitybase/v1/statements/batch` | Get batch statements for entities and properties. |
| ✅ | GET | `/health` | Health check endpoint for monitoring service status. |
| ✅ | POST | `/json-import` | Import entities from Wikidata JSONL dump file. |
| ✅ | GET | `/qualifiers/{hashes}` | Fetch qualifiers by hash(es). |
| ✅ | POST | `/redirects` | Create a redirect for an entity. |
| ✅ | GET | `/references/{hashes}` | Fetch references by hash(es). |
| ✅ | POST | `/representations/entities/lexemes` | Create a new lexeme entity. |
| ✅ | GET | `/representations/entities/lexemes/forms/{form_id}` | Get single form by ID (accepts L42-F1 or F1 format). |
| ✅ | DELETE | `/representations/entities/lexemes/forms/{form_id}` | Delete a form by ID. |
| ✅ | GET | `/representations/entities/lexemes/forms/{form_id}/representation` | Get all representations for a form. |
| ✅ | GET | `/representations/entities/lexemes/forms/{form_id}/representation/{langcode}` | Get representation for a form in specific language. |
| ✅ | PUT | `/representations/entities/lexemes/forms/{form_id}/representation/{langcode}` | Update form representation for language. |
| ✅ | DELETE | `/representations/entities/lexemes/forms/{form_id}/representation/{langcode}` | Delete form representation for language. |
| ✅ | GET | `/representations/entities/lexemes/senses/{sense_id}` | Get single sense by ID (accepts L42-S1 or S1 format). |
| ✅ | DELETE | `/representations/entities/lexemes/senses/{sense_id}` | Delete a sense by ID. |
| ✅ | GET | `/representations/entities/lexemes/senses/{sense_id}/glosses` | Get all glosses for a sense. |
| ✅ | GET | `/representations/entities/lexemes/senses/{sense_id}/glosses/{langcode}` | Get gloss for a sense in specific language. |
| ✅ | PUT | `/representations/entities/lexemes/senses/{sense_id}/glosses/{langcode}` | Update sense gloss for language. |
| ✅ | DELETE | `/representations/entities/lexemes/senses/{sense_id}/glosses/{langcode}` | Delete sense gloss for language. |
| ✅ | GET | `/representations/entities/lexemes/{lexeme_id}/forms` | List all forms for a lexeme, sorted by numeric suffix. |
| ✅ | GET | `/representations/entities/lexemes/{lexeme_id}/senses` | List all senses for a lexeme, sorted by numeric suffix. |
| ✅ | GET | `/representations/{hashes}` | Fetch form representations by hash(es). |
| ✅ | GET | `/representations/{hashes}` | Fetch sense glosses by hash(es). |
| ✅ | GET | `/snaks/{hashes}` | Fetch snaks by hash(es). |
| ✅ | POST | `/statements/batch` | Retrieve multiple statements by their content hashes in a batch request. |
| ✅ | POST | `/statements/cleanup-orphaned` | Clean up orphaned statements that are no longer referenced. |
| ✅ | GET | `/statements/most_used` | Get the most used statements based on reference count. |
| ✅ | GET | `/statements/{content_hash}` | Retrieve a single statement by its content hash. |
| ✅ | POST | `/statements/{statement_hash}/endorse` | Endorse a statement to signal trust. |
| ✅ | DELETE | `/statements/{statement_hash}/endorse` | Withdraw endorsement from a statement. |
| ✅ | GET | `/statements/{statement_hash}/endorsements` | Get endorsements for a statement. |
| ✅ | GET | `/statements/{statement_hash}/endorsements/stats` | Get endorsement statistics for a statement. |
| ✅ | GET | `/stats` | Get general wiki statistics. |
| ✅ | POST | `/users` | Create a new user. |
| ✅ | GET | `/users/stat` | Get user statistics. |
| ✅ | GET | `/users/{user_id}` | Get user information by MediaWiki user ID. |
| ✅ | GET | `/users/{user_id}/endorsements` | Get endorsements given by a user. |
| ✅ | GET | `/users/{user_id}/endorsements/stats` | Get endorsement statistics for a user. |
| ✅ | GET | `/users/{user_id}/thanks/received` | Get thanks received by user. |
| ✅ | GET | `/users/{user_id}/thanks/sent` | Get thanks sent by user. |
| ✅ | POST | `/users/{user_id}/watchlist` | Add a watchlist entry for user. |
| ✅ | GET | `/users/{user_id}/watchlist` | Get user's watchlist. |
| ✅ | GET | `/users/{user_id}/watchlist/notifications` | Get user's recent watchlist notifications. |
| ✅ | PUT | `/users/{user_id}/watchlist/notifications/{notification_id}/check` | Mark a notification as checked. |
| ✅ | POST | `/users/{user_id}/watchlist/remove` | Remove a watchlist entry for user. |
| ✅ | GET | `/users/{user_id}/watchlist/stats` | Get user's watchlist statistics. |
| ✅ | PUT | `/users/{user_id}/watchlist/toggle` | Enable or disable watchlist for user. |
| ✅ | DELETE | `/users/{user_id}/watchlist/{watch_id}` | Remove a watchlist entry by ID. |

| Status | Count |
|--------|-------|
| Implemented | 89 |
| Not Implemented | 0 |
| Total | 89 |
