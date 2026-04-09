# Data Models

> Request and Response models for the Entitybase API

---

## Entity Models

### EntityCreateRequest
Request model for entity creation.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Entity ID (e.g., Q42) - optional for creation, auto-assigned if not provided |
| `type` | string | Entity type (item, property, lexeme) *(required)* |
| `labels` | object | |
| `descriptions` | object | |
| `claims` | object | |
| `aliases` | object | |
| `sitelinks` | object | |
| `forms` | array[object] | |
| `senses` | array[object] | |
| `lemmas` | object | |
| `language` | string | Lexeme language (QID) |
| `lexical_category` | string | Lexeme lexical category (QID) |
| `is_mass_edit` | boolean | Whether this is a mass edit |
| `edit_type` | EditType | Classification of edit type |
| `is_locked` | boolean | Whether the entity is locked |
| `is_archived` | boolean | Whether the entity is archived |

---

### EntityResponse
Response model for entity data.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Entity ID. Example: 'Q42'. *(required)* |
| `rev_id` | integer | Revision ID of the entity. *(required)* |
| `data` | object | Full entity JSON data. *(required)* |

---

### EntityIdResult
Model for entity creation result with ID and revision.

| Field | Type | Description |
|-------|------|-------------|
| `entity_id` | string | The new entity ID (e.g., 'Q123') *(required)* |
| `revision_id` | integer | The revision ID of the created entity *(required)* |

---

### EntityState
Model for entity state information.

| Field | Type | Description |
|-------|------|-------------|
| `sp` | boolean | Whether the entity is semi-protected |
| `locked` | boolean | Whether the entity is locked |
| `archived` | boolean | Whether the entity is archived |
| `mep` | boolean | Whether the entity has mass edit protection |
| `deleted` | boolean | Whether the entity is deleted |

---

## Term Models

### TermUpdateRequest
Request body for updating entity terms (labels, descriptions, representations, glosses).

| Field | Type | Description |
|-------|------|-------------|
| `language` | string | Language code (e.g., 'en', 'fr') *(required)* |
| `value` | string | Term text value *(required)* |

---

### LabelResponse
Response model for entity labels.

| Field | Type | Description |
|-------|------|-------------|
| `value` | string | The label text for the specified language *(required)* |

---

### DescriptionResponse
Response model for entity descriptions.

| Field | Type | Description |
|-------|------|-------------|
| `value` | string | The description text for the specified language *(required)* |

---

### AliasesResponse
Response model for entity aliases.

| Field | Type | Description |
|-------|------|-------------|
| `aliases` | array[string] | List of alias texts for the specified language *(required)* |

---

## Statement Models

### AddStatementRequest
Request model for adding a single statement to an entity, form, or sense.

| Field | Type | Description |
|-------|------|-------------|
| `claim` | object | A valid Wikibase statement JSON. *(required)* |

---

### PatchStatementRequest
Request model for patching a statement.

| Field | Type | Description |
|-------|------|-------------|
| `claim` | object | The new claim data to replace the existing statement. *(required)* |

---

### StatementResponse
Response model for statement data.

| Field | Type | Description |
|-------|------|-------------|
| `schema` | string | Schema version for the statement. Example: '1.0'. *(required)* |
| `hash` | integer | Hash of the statement content. *(required)* |
| `statement` | object | Full statement JSON object. *(required)* |
| `created_at` | string | Timestamp when statement was created. *(required)* |

---

## User Models

### UserCreateRequest
Request to create/register a user.

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | integer | MediaWiki user ID *(required)* |

---

### UserResponse
User model.

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | integer | *(required)* |
| `created_at` | string | *(required)* |

---

### UserStatsResponse
API response for user statistics.

| Field | Type | Description |
|-------|------|-------------|
| `date` | string | Date of statistics computation. *(required)* |
| `total` | integer | Total number of users. *(required)* |
| `active` | integer | Number of active users. *(required)* |

---

## Watchlist Models

### WatchlistAddRequest
Request to add a watchlist entry.

| Field | Type | Description |
|-------|------|-------------|
| `entity_id` | string | Entity ID (e.g., Q42) *(required)* |
| `properties` | any | Specific properties to watch, empty for whole entity |

---

### WatchlistRemoveRequest
Request to remove a watchlist entry.

| Field | Type | Description |
|-------|------|-------------|
| `entity_id` | string | Entity ID to remove from watchlist *(required)* |
| `properties` | any | Specific properties to stop watching |

---

### WatchlistResponse
Response for listing user's watchlist.

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | integer | User ID for whom the watchlist is returned *(required)* |
| `watches` | array[object] | List of watchlist entries with entity_id and properties *(required)* |

---

## Sitelink Models

### SitelinkData
Data for a single sitelink.

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Page title *(required)* |
| `badges` | array[string] | List of badges |

---

### AllSitelinksResponse
Response model for all entity sitelinks.

| Field | Type | Description |
|-------|------|-------------|
| `sitelinks` | object | Dictionary mapping site key to sitelink data *(required)* |

---

## Lexeme Models

### FormCreateRequest
Request body for creating a new form.

| Field | Type | Description |
|-------|------|-------------|
| `representations` | object | Form representations by language code *(required)* |
| `grammatical_features` | array[string] | List of grammatical feature item IDs |
| `claims` | object | Optional statements/claims for the form |

---

### SenseCreateRequest
Request body for creating a new sense.

| Field | Type | Description |
|-------|------|-------------|
| `glosses` | object | Sense glosses by language code *(required)* |
| `claims` | object | Optional statements/claims for the sense |

---

### LexemeLanguageRequest
Request body for updating a lexeme's language.

| Field | Type | Description |
|-------|------|-------------|
| `language` | string | Lexeme language as QID (e.g., 'Q1860') *(required)* |

---

### LexemeLexicalCategoryRequest
Request body for updating a lexeme's lexical category.

| Field | Type | Description |
|-------|------|-------------|
| `lexical_category` | string | Lexeme lexical category as QID (e.g., 'Q1084') *(required)* |

---

## Endorsement Models

### EndorsementResponse
Response for endorsement operations.

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique identifier for the endorsement. *(required)* |
| `user_id` | integer | ID of the user who created the endorsement. *(required)* |
| `hash` | integer | Hash of the endorsed statement. *(required)* |
| `created_at` | string | Timestamp when the endorsement was created. *(required)* |

---

### EndorsementStatsResponse
Response for endorsement statistics.

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | integer | ID of the user for whom statistics are provided. *(required)* |
| `given` | integer | Total number of endorsements given by the user. *(required)* |
| `active` | integer | Number of active endorsements given by the user. *(required)* |

---

## Statistics Models

### GeneralStatsResponse
API response for general wiki statistics.

| Field | Type | Description |
|-------|------|-------------|
| `date` | string | Date of statistics computation. *(required)* |
| `total_statements` | integer | Total number of statements. *(required)* |
| `total_items` | integer | Total number of items. *(required)* |
| `total_lexemes` | integer | Total number of lexemes. *(required)* |
| `total_properties` | integer | Total number of properties. *(required)* |

---

### DeduplicationStatsByType
Deduplication stats for a single data type.

| Field | Type | Description |
|-------|------|-------------|
| `unique_hashes` | integer | Number of unique hashes stored *(required)* |
| `total_ref_count` | integer | Total reference count *(required)* |
| `deduplication_factor` | number | Deduplication factor as a percentage (0-100) *(required)* |
| `space_saved` | integer | Number of duplicates eliminated *(required)* |

---

## Other Models

### HealthCheckResponse
Detailed response model for health check.

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Overall health status *(required)* |
| `s3` | string | S3 service health status. *(required)* |
| `vitess` | string | Vitess service health status. *(required)* |
| `timestamp` | string | Timestamp of health check *(required)* |

---

### VersionResponse
Response model for version endpoint.

| Field | Type | Description |
|-------|------|-------------|
| `api_version` | string | API version *(required)* |
| `entitybase_version` | string | EntityBase version *(required)* |

---

### SettingsResponse
Response model for settings endpoint.

| Field | Type | Description |
|-------|------|-------------|
| `s3_endpoint` | string | *(required)* |
| `vitess_host` | string | *(required)* |
| `vitess_port` | integer | *(required)* |
| `log_level` | string | *(required)* |

---

## Related Links

- [← Back to API](../API.md)