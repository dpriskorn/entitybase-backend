# API Models Overview

## models/rest_api/response/entity/backlinks.py

### Backlink

Model representing a backlink from one entity to another.

**Fields**:

- `entity_id` (str): Entity ID that references the target
- `property_id` (str): Property used in the reference
- `rank` (str): Rank of the statement (normal/preferred/deprecated)

### BacklinksResponse

Response model for backlinks API.

**Fields**:

- `backlinks` (list[Backlink]): List of backlinks
- `limit` (int): Requested limit
- `offset` (int): Requested offset

## models/rest_api/response/entity/entitybase.py

### EntityDeleteResponse

Response model for entity deletion.

**Fields**:

- `id` (str): No description
- `revision_id` (int): No description
- `is_deleted` (bool): Whether entity is deleted
- `deletion_type` (str): Type of deletion performed
- `deletion_status` (str): Status of deletion (soft_deleted/hard_deleted)

### EntityHistoryEntry

Response model for a single entity history entry.

**Fields**:

- `revision_id` (int): No description
- `created_at` (str | None): No description
- `user_id` (int | None): No description
- `edit_summary` (str | None): No description

### EntityJsonImportResponse

Response model for JSONL entity import operations.

**Fields**:

- `processed_count` (int): Number of lines processed
- `imported_count` (int): Number of entities successfully imported
- `failed_count` (int): Number of entities that failed to import
- `error_log_path` (str): Path to error log file for malformed lines

### EntityListResponse

Response model for entity list queries.

**Fields**:

- `entities` (list[dict[str, Any]]): List of entities with their metadata
- `count` (int): Total number of entities returned

### EntityMetadataBatchResponse

Response model for batch entity metadata fetching.

**Fields**:

- `metadata` (dict[str, EntityMetadata | None]): Dictionary mapping entity_id to metadata or None

### EntityRedirectResponse

Response model for entity redirect creation.

**Fields**:

- `redirect_from_id` (str): No description
- `redirect_to_id` (str): No description
- `created_at` (str): No description
- `revision_id` (int): No description

### EntityResponse

Response model for entity data.

**Fields**:

- `id` (str): No description
- `revision_id` (int): No description
- `entity_data` (Dict[str, Any]): No description
- `is_semi_protected` (bool): No description
- `is_locked` (bool): No description
- `is_archived` (bool): No description
- `is_dangling` (bool): No description
- `is_mass_edit_protected` (bool): No description

### EntityRevisionResponse

Model for entity revision response.

**Fields**:

- `entity_id` (str): No description
- `revision_id` (int): No description
- `revision_data` (dict[str, Any]): Revision data

### ProtectionResponse

Model for entity protection information.

**Fields**:

- `is_semi_protected` (bool): Whether entity is semi-protected
- `is_locked` (bool): Whether entity is locked
- `is_archived` (bool): Whether entity is archived
- `is_dangling` (bool): Whether entity is dangling
- `is_mass_edit_protected` (bool): Whether entity is mass edit protected

## models/rest_api/response/entity/revert.py

### EntityRevertResponse

Response for entity revert operation.

**Fields**:

- `entity_id` (str): No description
- `new_revision_id` (int): No description
- `reverted_from_revision_id` (int): No description
- `reverted_at` (str): No description

## models/rest_api/response/entity/wikibase.py

### AliasValue

Individual alias entry with language and value.

**Fields**:

- `language` (str): No description
- `value` (str): No description

### DescriptionValue

Individual description entry with language and value.

**Fields**:

- `language` (str): No description
- `value` (str): No description

### EntityAliases

Collection of aliases keyed by language code.

**Fields**:

- `data` (dict[str, list[AliasValue]]): No description

### EntityDescriptions

Collection of descriptions keyed by language code.

**Fields**:

- `data` (dict[str, DescriptionValue]): No description

### EntityLabels

Collection of labels keyed by language code.

**Fields**:

- `data` (dict[str, LabelValue]): No description

### EntityMetadata

Model for entity metadata.

**Fields**:

- `id` (str): No description
- `type` (str): No description
- `labels` (EntityLabels): No description
- `descriptions` (EntityDescriptions): No description
- `aliases` (EntityAliases): No description
- `statements` (EntityStatements): No description
- `sitelinks` (EntitySitelinks): No description

### EntitySitelinks

Collection of sitelinks.

**Fields**:

- `data` (dict[str, Any]): No description

### EntityStatements

List of entity statements.

**Fields**:

- `data` (list[dict[str, Any]]): No description

### LabelValue

Individual label entry with language and value.

**Fields**:

- `language` (str): No description
- `value` (str): No description

### WikibaseEntityResponse

Response model for Wikibase REST API entity endpoints.

**Fields**:

- `id` (str): No description
- `type` (str): No description
- `labels` (Dict[str, Dict[str, str]]): No description
- `descriptions` (Dict[str, Dict[str, str]]): No description
- `aliases` (Dict[str, List[Dict[str, str]]]): No description
- `claims` (Dict[str, List[Dict[str, Any]]]): No description
- `sitelinks` (Dict[str, Dict[str, Any]]): No description

## models/rest_api/response/health.py

### HealthCheckResponse

Detailed response model for health check.

**Fields**:

- `status` (str): No description
- `s3` (str): No description
- `vitess` (str): No description

### HealthResponse

Response model for health check.

**Fields**:

- `status` (str): No description

### WorkerHealthCheck

Model for worker health check response.

**Fields**:

- `status` (str): Health status: healthy or unhealthy
- `worker_id` (str): Unique worker identifier
- `range_status` (dict[str, Any]): Current ID range allocation status

## models/rest_api/response/id_response.py

### IdResponse

Response model for generated entity ID.

**Fields**:

- `id` (str): The generated entity ID (e.g., 'Q123', 'P456')

## models/rest_api/response/misc.py

### Aliases

Model for extracted aliases dictionary.

**Fields**:

- `aliases` (dict[str, list[str]]): Aliases per language

### AliasesResponse

Response model for entity aliases.

**Fields**:

- `aliases` (list[str]): List of alias texts for the specified language

### BacklinkStatisticsData

Container for computed backlink statistics.

**Fields**:

- `total_backlinks` (int): Total number of backlink relationships
- `unique_entities_with_backlinks` (int): Number of entities with at least one backlink
- `top_entities_by_backlinks` (list[TopEntityByBacklinks]): Top entities by backlink count

### BacklinkStatisticsResponse

API response for backlink statistics.

**Fields**:

- `date` (str): Date of statistics computation
- `total_backlinks` (int): Total number of backlink relationships
- `unique_entities_with_backlinks` (int): Number of entities with at least one backlink
- `top_entities_by_backlinks` (list[TopEntityByBacklinks]): Top entities by backlink count

### CleanupOrphanedResponse

**Fields**:

- `cleaned_count` (int): Number of statements cleaned up from S3 and Vitess
- `failed_count` (int): Number of statements that failed to clean up
- `errors` (list[str]): List of error messages for failed cleanups

### DescriptionResponse

Response model for entity descriptions.

**Fields**:

- `value` (str): The description text for the specified language

### DescriptionsResponse

Response model for all entity descriptions.

**Fields**:

- `descriptions` (dict[str, str]): Descriptions per language

### EntitiesResponse

Response model for entities search.

**Fields**:

- `entities` (dict[str, Any]): Entities data

### EntityListing

Model for entity listing entries.

**Fields**:

- `entity_id` (str): Entity ID
- `entity_type` (str): Entity type (Q, P, etc.)
- `reason` (str | None): Reason for listing

### JsonSchema

Model for JSON schema data.

**Fields**:

- `data` (dict[str, Any]): The JSON schema dictionary

### LabelResponse

Response model for entity labels.

**Fields**:

- `value` (str): The label text for the specified language

### LabelsResponse

Response model for all entity labels.

**Fields**:

- `labels` (dict[str, str]): Labels per language

### MetadataContent

Model for metadata content.

**Fields**:

- `ref_count` (int): Reference count

### PropertiesResponse

Response model for entity properties.

**Fields**:

- `properties` (dict[str, Any]): Entity properties

### RangeStatus

Model for ID range status.

**Fields**:

- `current_start` (int): Current range start ID
- `current_end` (int): Current range end ID
- `next_id` (int): Next available ID
- `ids_used` (int): Number of IDs used
- `utilization` (float): Utilization percentage

### RangeStatuses

Model for all ID range statuses.

**Fields**:

- `ranges` (dict[str, RangeStatus]): Range statuses by entity type

### RawEntityData

Model for raw entity data from external APIs.

**Fields**:

- `data` (dict[str, Any]): Raw entity data

### RawRevisionResponse

Response model for raw revision data.

**Fields**:

- `data` (dict[str, Any]): Raw revision data from storage

### RevisionMetadataResponse

Metadata for entity revisions.

**Fields**:

- `revision_id` (int): No description
- `created_at` (str): No description
- `user_id` (int): No description
- `edit_summary` (str): No description

### SitelinksResponse

Response model for all entity sitelinks.

**Fields**:

- `sitelinks` (dict[str, str]): Sitelinks per site

### TermsResponse

Model for batch terms result.

**Fields**:

- `terms` (dict[int, tuple[str, str]]): Terms by hash

### TopEntityByBacklinks

Model for entity backlink ranking.

**Fields**:

- `entity_id` (str): Entity ID
- `backlink_count` (int): Number of backlinks to this entity

### WatchCounts

Model for user watch counts.

**Fields**:

- `entity_count` (int): Number of entities watched
- `property_count` (int): Number of properties watched

## models/rest_api/response/rdf.py

### DeduplicationStats

Model for deduplication cache statistics.

**Fields**:

- `hits` (int): Number of cache hits
- `misses` (int): Number of cache misses
- `size` (int): Current cache size
- `collision_rate` (float): Collision rate percentage

### FullRevisionData

Model for full revision data from database.

**Fields**:

- `revision_id` (int): Revision ID
- `statements` (list[int]): List of statement hashes
- `properties` (list[str]): List of unique properties
- `property_counts` (dict[str, int]): Property counts
- `labels` (dict[str, dict[str, str]]): Entity labels
- `descriptions` (dict[str, dict[str, str]]): Entity descriptions
- `aliases` (dict[str, list[str]]): Entity aliases
- `sitelinks` (dict[str, dict[str, str]]): Entity sitelinks

### MetadataLoadResponse

Response model for metadata loading operations.

**Fields**:

- `results` (dict[str, bool]): Dictionary mapping entity_id to success status

### RedirectBatchResponse

Response model for batch entity redirects fetching.

**Fields**:

- `redirects` (dict[str, list[str]]): Dictionary mapping entity_id to list of redirect titles

### WikibasePredicates

Model for Wikibase predicate URIs for a property.

**Fields**:

- `direct` (str): Direct property predicate
- `statement` (str): Statement property predicate
- `statement_value` (str): Statement value property predicate
- `qualifier` (str): Qualifier property predicate
- `reference` (str): Reference property predicate
- `statement_value_node` (str): Statement value node predicate

## models/rest_api/response/statement.py

### MostUsedStatementsResponse

**Fields**:

- `statements` (list[int]): List of statement hashes sorted by ref_count DESC

### PropertyCounts

Model for property statement counts.

**Fields**:

- `counts` (dict[str, int]): Dictionary mapping property ID to statement count

### PropertyCountsResponse

**Fields**:

- `property_counts` (dict[str, int]): Dict mapping property ID -> statement count

### PropertyHashesResponse

**Fields**:

- `property_hashes` (list[int]): List of statement hashes for specified properties

### PropertyListResponse

**Fields**:

- `properties` (list[str]): List of unique property IDs

### StatementBatchResponse

Response model for batch statement queries.

**Fields**:

- `statements` (list[StatementResponse]): List of statements
- `not_found` (list[int]): Hashes that were not found

### StatementHashResult

**Fields**:

- `statements` (list[int]): List of statement hashes (rapidhash of each statement)
- `properties` (list[str]): Sorted list of unique property IDs
- `property_counts` (dict[str, int]): Dict mapping property ID -> count of statements
- `full_statements` (list[Dict[str, Any]]): List of full statement dicts (parallel with hashes)

### StatementResponse

Response model for statement data.

**Fields**:

- `schema_version` (str): Schema version
- `content_hash` (int): Statement hash
- `statement` (Dict[str, Any]): Full statement JSON
- `created_at` (str): Creation timestamp

### StatementsResponse

Response model for statements.

**Fields**:

- `statements` (dict[str, Any]): Statements data

## models/rest_api/response/user.py

### MessageResponse

Generic message response.

**Fields**:

- `message` (str): No description

### UserCreateResponse

Response for user creation.

**Fields**:

- `user_id` (int): No description
- `created` (bool): No description

### WatchlistToggleResponse

Response for watchlist toggle.

**Fields**:

- `user_id` (int): No description
- `enabled` (bool): No description

## models/rest_api/response/user_activity.py

### UserActivityResponse

Response for user activity query.

**Fields**:

- `user_id` (int): No description
- `activities` (List[UserActivityItem]): No description

## models/rest_api/response/user_preferences.py

### UserPreferencesResponse

Response for user preferences query.

**Fields**:

- `user_id` (int): No description
- `notification_limit` (int): No description
- `retention_hours` (int): No description

