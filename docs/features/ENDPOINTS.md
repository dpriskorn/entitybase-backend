# REST API Endpoints

This API has 126 endpoints implemented, covering entity management (items, properties, lexemes), lexeme components (forms, senses, lemmas, glosses), entity terms (labels, descriptions, aliases), statements and claims, sitelinks, revision history, user management, and batch resolution endpoints.

| Implemented | Method | Full Path | Description |
|-------------|--------|-----------|-------------|
| ✅ | GET | `/debug/entity/{entity_id}` | Debug endpoint to check entity in database. |
| ✅ | GET | `/debug/entity_head/{entity_id}` | Debug endpoint to check entity_head table. |
| ✅ | GET | `/entities` | List entities based on type, status, edit_type, limit, and offset. |
| ✅ | GET | `/entities/items` | List all items (Q-prefixed entities). |
| ✅ | POST | `/entities/items` | Create a new empty item entity. |
| ✅ | GET | `/entities/lexemes` | List all lexemes (L-prefixed entities). |
| ✅ | POST | `/entities/lexemes` | Create a new lexeme entity. |
| ✅ | GET | `/entities/lexemes/forms/{form_id}` | Get single form by ID (accepts L42-F1 or F1 format). |
| ✅ | DELETE | `/entities/lexemes/forms/{form_id}` | Delete a form by ID. |
| ✅ | GET | `/entities/lexemes/forms/{form_id}/representation` | Get all representations for a form. |
| ✅ | GET | `/entities/lexemes/forms/{form_id}/representation/{langcode}` | Get representation for a form in specific language. |
| ✅ | POST | `/entities/lexemes/forms/{form_id}/representation/{langcode}` | Add a new form representation for language. |
| ✅ | PUT | `/entities/lexemes/forms/{form_id}/representation/{langcode}` | Update form representation for language. |
| ✅ | DELETE | `/entities/lexemes/forms/{form_id}/representation/{langcode}` | Delete form representation for language. |
| ✅ | POST | `/entities/lexemes/forms/{form_id}/statements` | Add a statement to a form. |
| ✅ | GET | `/entities/lexemes/senses/{sense_id}` | Get single sense by ID (accepts L42-S1 or S1 format). |
| ✅ | DELETE | `/entities/lexemes/senses/{sense_id}` | Delete a sense by ID. |
| ✅ | GET | `/entities/lexemes/senses/{sense_id}/glosses` | Get all glosses for a sense. |
| ✅ | GET | `/entities/lexemes/senses/{sense_id}/glosses/{langcode}` | Get gloss for a sense in specific language. |
| ✅ | POST | `/entities/lexemes/senses/{sense_id}/glosses/{langcode}` | Add a new sense gloss for a language. |
| ✅ | PUT | `/entities/lexemes/senses/{sense_id}/glosses/{langcode}` | Update sense gloss for language. |
| ✅ | DELETE | `/entities/lexemes/senses/{sense_id}/glosses/{langcode}` | Delete sense gloss for language. |
| ✅ | POST | `/entities/lexemes/senses/{sense_id}/statements` | Add a statement to a sense. |
| ✅ | GET | `/entities/lexemes/{lexeme_id}/forms` | List all forms for a lexeme, sorted by numeric suffix. |
| ✅ | POST | `/entities/lexemes/{lexeme_id}/forms` | Create a new form for a lexeme. |
| ✅ | GET | `/entities/lexemes/{lexeme_id}/language` | Get the language of a lexeme. |
| ✅ | PUT | `/entities/lexemes/{lexeme_id}/language` | Update the language of a lexeme. |
| ✅ | GET | `/entities/lexemes/{lexeme_id}/lemmas` | Get all lemmas for a lexeme. |
| ✅ | GET | `/entities/lexemes/{lexeme_id}/lemmas/{langcode}` | Get lemma for a lexeme in specific language. |
| ✅ | POST | `/entities/lexemes/{lexeme_id}/lemmas/{langcode}` | Add a new lemma for language. |
| ✅ | PUT | `/entities/lexemes/{lexeme_id}/lemmas/{langcode}` | Update lemma for language. |
| ✅ | DELETE | `/entities/lexemes/{lexeme_id}/lemmas/{langcode}` | Delete lemma for language. |
| ✅ | GET | `/entities/lexemes/{lexeme_id}/lexicalcategory` | Get the lexical category of a lexeme. |
| ✅ | PUT | `/entities/lexemes/{lexeme_id}/lexicalcategory` | Update the lexical category of a lexeme. |
| ✅ | GET | `/entities/lexemes/{lexeme_id}/senses` | List all senses for a lexeme, sorted by numeric suffix. |
| ✅ | POST | `/entities/lexemes/{lexeme_id}/senses` | Create a new sense for a lexeme. |
| ✅ | GET | `/entities/properties` | List all properties (P-prefixed entities). |
| ✅ | POST | `/entities/properties` | Create a new empty property entity. |
| ✅ | GET | `/entities/{entity_id}` | Retrieve a single entity by its ID. |
| ✅ | DELETE | `/entities/{entity_id}` | Delete an entity. |
| ✅ | GET | `/entities/{entity_id}.json` | Get entity data in JSON format. |
| ✅ | GET | `/entities/{entity_id}.ttl` | Get entity data in Turtle format. |
| ✅ | GET | `/entities/{entity_id}/aliases/{language_code}` | Get entity alias texts for language. |
| ✅ | PUT | `/entities/{entity_id}/aliases/{language_code}` | Update entity aliases for language. |
| ✅ | POST | `/entities/{entity_id}/aliases/{language_code}` | Add a single alias to entity for language. |
| ✅ | DELETE | `/entities/{entity_id}/aliases/{language_code}` | Delete all aliases for entity language. |
| ✅ | POST | `/entities/{entity_id}/archive` | Archive an entity. |
| ✅ | DELETE | `/entities/{entity_id}/archive` | Unarchive an entity. |
| ✅ | GET | `/entities/{entity_id}/backlinks` | Get backlinks for an entity. |
| ✅ | GET | `/entities/{entity_id}/descriptions/{language_code}` | Get entity description text for language. |
| ✅ | PUT | `/entities/{entity_id}/descriptions/{language_code}` | Update entity description for language. |
| ✅ | DELETE | `/entities/{entity_id}/descriptions/{language_code}` | Delete entity description for language. |
| ✅ | POST | `/entities/{entity_id}/descriptions/{language_code}` | Add a new description to entity for language (alias for PUT). |
| ✅ | GET | `/entities/{entity_id}/labels/{language_code}` | Get entity label text for language. |
| ✅ | PUT | `/entities/{entity_id}/labels/{language_code}` | Update entity label for language. |
| ✅ | DELETE | `/entities/{entity_id}/labels/{language_code}` | Delete entity label for language. |
| ✅ | POST | `/entities/{entity_id}/labels/{language_code}` | Add a new label to entity for language (alias for PUT). |
| ✅ | POST | `/entities/{entity_id}/lock` | Lock an entity from edits. |
| ✅ | DELETE | `/entities/{entity_id}/lock` | Remove lock from an entity. |
| ✅ | POST | `/entities/{entity_id}/mass-edit-protect` | Add mass edit protection to an entity. |
| ✅ | DELETE | `/entities/{entity_id}/mass-edit-protect` | Remove mass edit protection from an entity. |
| ✅ | GET | `/entities/{entity_id}/properties` | Get list of unique property IDs for an entity's head revision. |
| ✅ | POST | `/entities/{entity_id}/properties/{property_id}` | Add claims for a single property to an entity. |
| ✅ | GET | `/entities/{entity_id}/properties/{property_list}` | Get entity property hashes for specified properties. |
| ✅ | GET | `/entities/{entity_id}/property_counts` | Get statement counts per property for an entity's head revision. |
| ✅ | POST | `/entities/{entity_id}/revert` | Revert entity to a previous revision. |
| ✅ | POST | `/entities/{entity_id}/revert-redirect` | No description |
| ✅ | GET | `/entities/{entity_id}/revision/{revision_id}` | Get a specific revision of an entity. |
| ✅ | GET | `/entities/{entity_id}/revision/{revision_id}/json` | Get JSON representation of a specific entity revision. |
| ✅ | GET | `/entities/{entity_id}/revision/{revision_id}/ttl` | Get Turtle (TTL) representation of a specific entity revision. |
| ✅ | GET | `/entities/{entity_id}/revisions` | Get the revision history for an entity. |
| ✅ | POST | `/entities/{entity_id}/revisions/{revision_id}/thank` | Send a thank for a specific revision. |
| ✅ | GET | `/entities/{entity_id}/revisions/{revision_id}/thanks` | Get all thanks for a specific revision. |
| ✅ | POST | `/entities/{entity_id}/semi-protect` | Semi-protect an entity. |
| ✅ | DELETE | `/entities/{entity_id}/semi-protect` | Remove semi-protection from an entity. |
| ✅ | GET | `/entities/{entity_id}/sitelinks` | Get all sitelinks for an entity. |
| ✅ | GET | `/entities/{entity_id}/sitelinks/{site}` | Get a single sitelink for an entity. |
| ✅ | POST | `/entities/{entity_id}/sitelinks/{site}` | Add a new sitelink for an entity. |
| ✅ | PUT | `/entities/{entity_id}/sitelinks/{site}` | Update an existing sitelink for an entity. |
| ✅ | DELETE | `/entities/{entity_id}/sitelinks/{site}` | Delete a sitelink from an entity. |
| ✅ | POST | `/entities/{entity_id}/statements` | Add a single statement to an entity. |
| ✅ | DELETE | `/entities/{entity_id}/statements/{statement_hash}` | Remove a statement by hash from an entity. |
| ✅ | PATCH | `/entities/{entity_id}/statements/{statement_hash}` | Replace a statement by hash with new claim data. |
| ✅ | GET | `/entity/{entity_id}/properties/{property_list}` | Get statement hashes for specified properties in an entity. |
| ✅ | GET | `/health` | Health check endpoint for monitoring service status. |
| ✅ | POST | `/import` | Import a single entity of any type. |
| ✅ | POST | `/redirects` | Create a redirect for an entity. |
| ✅ | GET | `/resolve/aliases/{hashes}` | Get batch aliases by hashes. |
| ✅ | GET | `/resolve/descriptions/{hashes}` | Get batch descriptions by hashes. |
| ✅ | GET | `/resolve/glosses/{hashes}` | Fetch sense glosses by hash(es). |
| ✅ | GET | `/resolve/labels/{hashes}` | Get batch labels by hashes. |
| ✅ | GET | `/resolve/qualifiers/{hashes}` | Fetch qualifiers by hash(es). |
| ✅ | GET | `/resolve/references/{hashes}` | Fetch references by hash(es). |
| ✅ | GET | `/resolve/representations/{hashes}` | Fetch form representations by hash(es). |
| ✅ | GET | `/resolve/sitelinks/{hashes}` | Get batch sitelink titles by hashes. |
| ✅ | GET | `/resolve/snaks/{hashes}` | Fetch snaks by hash(es). |
| ✅ | GET | `/resolve/statements/{hashes}` | Fetch statements by hash(es). |
| ✅ | GET | `/settings` | Get current application settings (excludes sensitive values). |
| ✅ | GET | `/statements/batch` | Get statement hashes for multiple entities. |
| ✅ | POST | `/statements/cleanup-orphaned` | Clean up orphaned statements that are no longer referenced. |
| ✅ | GET | `/statements/most_used` | Get most used statements based on reference count. |
| ✅ | GET | `/statements/{content_hash}` | Retrieve a single statement by its content hash. |
| ✅ | POST | `/statements/{statement_hash}/endorse` | Endorse a statement to signal trust. |
| ✅ | DELETE | `/statements/{statement_hash}/endorse` | Withdraw endorsement from a statement. |
| ✅ | GET | `/statements/{statement_hash}/endorsements` | Get endorsements for a statement. |
| ✅ | GET | `/statements/{statement_hash}/endorsements/stats` | Get endorsement statistics for a statement. |
| ✅ | GET | `/stats` | Get general wiki statistics. |
| ✅ | GET | `/stats/deduplication` | Get deduplication statistics for all data types. |
| ✅ | POST | `/users` | Create a new user. |
| ✅ | GET | `/users/stat` | Get user statistics. |
| ✅ | GET | `/users/{user_id}` | Get user information by MediaWiki user ID. |
| ✅ | DELETE | `/users/{user_id}` | Delete a user by ID. |
| ✅ | GET | `/users/{user_id}/activity` | Get user's activity with filtering. |
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
| ✅ | GET | `/version` | Return API and EntityBase versions. |
