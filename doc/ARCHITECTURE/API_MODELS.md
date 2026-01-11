# API Models Overview

## models/rest_api/response/entity.py

### AliasValue

Individual alias entry with language and value.

**Fields**:

- `language` (str): No description
- `value` (str): No description

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

### DescriptionValue

Individual description entry with language and value.

**Fields**:

- `language` (str): No description
- `value` (str): No description

### EntityAliases

Collection of aliases keyed by language code.

**Fields**:

- `data` (dict[str, list[AliasValue]]): No description

### EntityDeleteResponse

Response model for entity deletion.

**Fields**:

- `id` (str): No description
- `revision_id` (int): No description
- `is_deleted` (bool): Whether entity is deleted
- `deletion_type` (str): Type of deletion performed
- `deletion_status` (str): Status of deletion (soft_deleted/hard_deleted)

### EntityDescriptions

Collection of descriptions keyed by language code.

**Fields**:

- `data` (dict[str, DescriptionValue]): No description

### EntityJsonImportResponse

Response model for JSONL entity import operations.

**Fields**:

- `processed_count` (int): Number of lines processed
- `imported_count` (int): Number of entities successfully imported
- `failed_count` (int): Number of entities that failed to import
- `error_log_path` (str): Path to error log file for malformed lines

### EntityLabels

Collection of labels keyed by language code.

**Fields**:

- `data` (dict[str, LabelValue]): No description

### EntityListResponse

Response model for entity list queries.

**Fields**:

- `entities` (list[dict[str, Any]]): List of entities with their metadata
- `count` (int): Total number of entities returned

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
- `data` (Dict[str, Any]): No description
- `is_semi_protected` (bool): No description
- `is_locked` (bool): No description
- `is_archived` (bool): No description
- `is_dangling` (bool): No description
- `is_mass_edit_protected` (bool): No description

### EntityRevisionResponse

Model for entity revision response.

**Fields**:

- `entity_id` (str): Entity ID
- `revision_id` (int): Revision ID
- `data` (dict[str, Any]): Revision data

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

### ProtectionInfo

Model for entity protection information.

**Fields**:

- `is_semi_protected` (bool): Whether entity is semi-protected
- `is_locked` (bool): Whether entity is locked
- `is_archived` (bool): Whether entity is archived
- `is_dangling` (bool): Whether entity is dangling
- `is_mass_edit_protected` (bool): Whether entity is mass edit protected

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

### AliasesDict

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

### JsonSchema

Model for JSON schema data.

**Fields**:

- `data` (dict[str, Any]): The JSON schema dictionary

### LabelResponse

Response model for entity labels.

**Fields**:

- `value` (str): The label text for the specified language

### MetadataContent

Model for metadata content.

**Fields**:

- `ref_count` (int): Reference count

### RawRevisionResponse

Response model for raw revision data.

**Fields**:

- `data` (dict[str, Any]): Raw revision data from storage

### RevisionMetadataResponse

Metadata for entity revisions.

**Fields**:

- `revision_id` (int): No description
- `created_at` (str): No description

### TopEntityByBacklinks

Model for entity backlink ranking.

**Fields**:

- `entity_id` (str): Entity ID
- `backlink_count` (int): Number of backlinks to this entity

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

