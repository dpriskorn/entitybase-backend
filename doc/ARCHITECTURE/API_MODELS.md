# API Models Overview

## models/data/rest_api/v1/entitybase/response/endorsements.py

### BatchEndorsementStatsResponse

Response for batch statement endorsement statistics.

**Fields**:

- `stats` (List[StatementEndorsementStats]): List of endorsement statistics for multiple statements

### EndorsementListResponse

Response for endorsement list queries.

**Fields**:

- `statement_hash` (int): Hash of the statement for which endorsements are listed. Example: 12345
- `user_id` (int): ID of the user whose endorsements are listed. Example: 67890
- `endorsements` (List[EndorsementResponse]): List of endorsements. Example: [{'id': 1, 'user_id': 123}]
- `total_count` (int): Total number of endorsements. Example: 50
- `has_more` (bool): Whether there are more endorsements to fetch. Example: true
- `stats` (Optional['StatementEndorsementStats']): Statistics for the statement's endorsements

### EndorsementResponse

Response for endorsement operations.

**Fields**:

- `endorsement_id` (int): Unique identifier for the endorsement. Example: 12345.
- `user_id` (int): ID of the user who created the endorsement. Example: 67890.
- `statement_hash` (int): Hash of the endorsed statement. Example: 987654321.
- `created_at` (str): Timestamp when the endorsement was created (ISO format). Example: '2023-01-01T12:00:00Z'.
- `removed_at` (str): Timestamp when the endorsement was removed (ISO format), empty string if active. Example: '2023-12-31T23:59:59Z'.

### EndorsementStatsResponse

Response for endorsement statistics.

**Fields**:

- `user_id` (int): ID of the user for whom statistics are provided. Example: 12345
- `total_endorsements_given` (int): Total number of endorsements given by the user. Example: 10
- `total_endorsements_active` (int): Number of active endorsements given by the user. Example: 8

### SingleEndorsementStatsResponse

Response for single statement endorsement statistics.

**Fields**:

- `total` (int): Total number of endorsements for the statement. Example: 15
- `active` (int): Number of active endorsements for the statement. Example: 12
- `withdrawn` (int): Number of withdrawn endorsements for the statement. Example: 3

### StatementEndorsementResponse

Endorsement record.

**Fields**:

- `id` (int): Unique identifier for the endorsement
- `user_id` (int): ID of the user who gave the endorsement
- `statement_hash` (int): Hash of the endorsed statement
- `created_at` (datetime): Timestamp when the endorsement was created
- `removed_at` (Optional[datetime]): Timestamp when the endorsement was removed, null if active

### StatementEndorsementStats

Response for statement endorsement statistics.

**Fields**:

- `total` (int): Total number of endorsements for the statement. Example: 15
- `active` (int): Number of active endorsements for the statement. Example: 12
- `withdrawn` (int): Number of withdrawn endorsements for the statement. Example: 3

## models/data/rest_api/v1/entitybase/response/entity/backlink_statistics.py

### BacklinkStatisticsData

Container for computed backlink statistics.

**Fields**:

- `total_backlinks` (int): Total number of backlink relationships. Example: 150.
- `unique_entities_with_backlinks` (int): Number of entities with at least one backlink. Example: 75.
- `top_entities_by_backlinks` (list[TopEntityByBacklinks]): Top entities by backlink count. Example: [{'entity_id': 'Q1', 'backlink_count': 10}].

### BacklinkStatisticsResponse

API response for backlink statistics.

**Fields**:

- `date` (str): Date of statistics computation. Example: '2023-01-01'.
- `total_backlinks` (int): Total number of backlink relationships. Example: 150.
- `unique_entities_with_backlinks` (int): Number of entities with at least one backlink. Example: 75.
- `top_entities_by_backlinks` (list[TopEntityByBacklinks]): Top entities by backlink count. Example: [{'entity_id': 'Q1', 'backlink_count': 10}].

## models/data/rest_api/v1/entitybase/response/entity/backlinks.py

### BacklinkResponse

Model representing a backlink from one entity to another.

**Fields**:

- `entity_id` (str): Entity ID that references the target
- `property_id` (str): Property used in the reference
- `rank` (str): Rank of the statement (normal/preferred/deprecated)

### BacklinksResponse

Response model for backlinks API.

**Fields**:

- `backlinks` (list[BacklinkResponse]): List of backlinks
- `limit` (int): Requested limit
- `offset` (int): Requested offset

## models/data/rest_api/v1/entitybase/response/entity/change.py

### EntityChange

Schema for entity change events in API responses.

**Fields**:

- `entity_id` (str): The ID of the entity that changed
- `revision_id` (int): The new revision ID after the change
- `change_type` ('ChangeType'): The type of change
- `from_revision_id` (int): The previous revision ID (0 for creations)
- `changed_at` (datetime): Timestamp of the change
- `edit_summary` (str): Summary of the edit

## models/data/rest_api/v1/entitybase/response/entity/entitybase.py

### EntityAliasesResponse

Collection of aliases keyed by language code.

**Fields**:

- `data` (dict[str, list[AliasValue]]): Dictionary of aliases keyed by language code.

### EntityDeleteResponse

Response model for entity deletion.

**Fields**:

- `id` (str): Entity ID. Example: 'Q42'.
- `revision_id` (int): Revision ID at deletion. Example: 12345.
- `is_deleted` (bool): Whether entity is deleted. Example: true.
- `deletion_type` (str): Type of deletion performed. Example: 'soft_delete'.
- `deletion_status` (str): Status of deletion (soft_deleted/hard_deleted). Example: 'soft_deleted'.

### EntityDescriptionsResponse

Collection of descriptions keyed by language code.

**Fields**:

- `data` (dict[str, DescriptionValue]): Dictionary of descriptions keyed by language code. Example: {'en': {'language': 'en', 'value': 'A test description'}}.

### EntityHistoryEntry

Response model for a single entity history entry.

**Fields**:

- `revision_id` (int): Revision ID. Example: 12345.
- `created_at` (str): Creation timestamp (ISO format). Example: '2023-01-01T12:00:00Z'.
- `user_id` (int): User ID who made the change. Example: 67890.
- `edit_summary` (str): Edit summary text. Example: 'Added label'.

### EntityJsonImportResponse

Response model for JSONL entity import operations.

**Fields**:

- `processed_count` (int): Number of lines processed
- `imported_count` (int): Number of entities successfully imported
- `failed_count` (int): Number of entities that failed to import
- `error_log_path` (str): Path to error log file for malformed lines

### EntityLabelsResponse

Collection of labels keyed by language code.

**Fields**:

- `data` (dict[str, LabelValue]): Dictionary of labels keyed by language code. Example: {'en': {'language': 'en', 'value': 'Test'}}.

### EntityListResponse

Response model for entity list queries.

**Fields**:

- `entities` (list[dict[str, Any]]): List of entities with their metadata
- `count` (int): Total number of entities returned

### EntityMetadataBatchResponse

Response model for batch entity metadata fetching.

**Fields**:

- `metadata` (dict[str, EntityMetadataResponse | None]): Dictionary mapping entity_id to metadata or None

### EntityMetadataResponse

Model for entity metadata.

**Fields**:

- `id` (str): Entity ID
- `type` (str): Entity type
- `labels` (EntityLabelsResponse): Entity labels
- `descriptions` (EntityDescriptionsResponse): Entity descriptions
- `aliases` (EntityAliasesResponse): Entity aliases
- `statements` (EntityStatementsResponse): Entity statements
- `sitelinks` (EntitySitelinksResponse): Entity sitelinks

### EntityRedirectResponse

Response model for entity redirect creation.

**Fields**:

- `redirect_from_id` (str): Entity ID being redirected from
- `redirect_to_id` (str): Entity ID being redirected to
- `created_at` (str): Creation timestamp of the redirect
- `revision_id` (int): Revision ID of the redirect

### EntityResponse

Response model for entity data.

**Fields**:

- `id` (str): Entity ID. Example: 'Q42'.
- `revision_id` (int): Revision ID of the entity. Example: 12345.
- `entity_data` (S3RevisionData): Full entity JSON data. Example: {'id': 'Q42', 'type': 'item'}.
- `state` (EntityState | None): Entity state information (optional, may be None for revisions).

### EntitySitelinksResponse

Collection of sitelinks.

**Fields**:

- `data` (dict[str, SitelinkValue]): Dictionary of sitelinks keyed by site.

### EntityStatementsResponse

List of entity statements.

**Fields**:

- `data` (list[dict[str, Any]]): List of entity statements.

### ProtectionResponse

Model for entity protection information.

**Fields**:

- `is_semi_protected` (bool): Whether entity is semi-protected. Example: true.
- `is_locked` (bool): Whether entity is locked. Example: false.
- `is_archived` (bool): Whether entity is archived. Example: false.
- `is_dangling` (bool): Whether entity is dangling. Example: false.
- `is_mass_edit_protected` (bool): Whether entity is mass edit protected. Example: true.

## models/data/rest_api/v1/entitybase/response/entity/revert.py

### EntityRevertResponse

Response for entity revert operation.

**Fields**:

- `entity_id` (str): ID of the reverted entity. Example: 'Q42'.
- `new_revision_id` (int): New revision ID after revert. Example: 12345.
- `reverted_from_revision_id` (int): Original revision ID before revert. Example: 67890.
- `reverted_at` (str): Timestamp of the revert. Example: '2023-01-01T12:00:00Z'.

## models/data/rest_api/v1/entitybase/response/entity/revision_read_response.py

### RevisionReadResponse

Response model for reading revisions.

**Fields**:

- `entity_id` (str): No description
- `revision_id` (int): No description
- `data` (RevisionData): No description
- `content` (dict[str, Any]): No description
- `schema_version` (str): No description
- `created_at` (str): No description
- `user_id` (int): No description
- `edit_summary` (str): No description
- `redirects_to` (str): No description

## models/data/rest_api/v1/entitybase/response/entity/wikibase.py

### AliasValue

Individual alias entry with language and value.

**Fields**:

- `language` (str): Language code for the alias. Example: 'en'.
- `value` (str): The alias text. Example: 'Alternative Name'.

### DescriptionValue

Individual description entry with language and value.

**Fields**:

- `language` (str): Language code for the description. Example: 'en'.
- `value` (str): The description text. Example: 'A test description'.

### LabelValue

Individual label entry with language and value.

**Fields**:

- `language` (str): Language code for the label. Example: 'en'.
- `value` (str): The label text. Example: 'Test Label'.

### SitelinkValue

Individual sitelink entry.

**Fields**:

- `site` (str): Site identifier for the sitelink. Example: 'enwiki'.
- `title` (str): Page title on the site. Example: 'Test Page'.
- `url` (str): URL of the page. Example: 'https://en.wikipedia.org/wiki/Test_Page'.
- `badges` (List[str]): List of badges associated with the sitelink. Example: ['featuredarticle']

## models/data/rest_api/v1/entitybase/response/events.py

### RDFChangeEvent

RDF change event following MediaWiki recentchange schema.

**Fields**:

- `schema_uri` (str): Schema URI for this event
- `meta` (dict): Event metadata
- `entity_id` (str): Entity ID (e.g., Q42)
- `revision_id` (int): New revision ID
- `from_revision_id` (int): Previous revision ID (0 for creation)
- `added_triples` (list[tuple[str, str, str]]): RDF triples added in this revision
- `removed_triples` (list[tuple[str, str, str]]): RDF triples removed in this revision
- `canonicalization_method` (str): RDF canonicalization method used
- `triple_count_diff` (int): Net change in triple count
- `type` (str): Type of change
- `title` (str): Entity title
- `user` (str): Editor username
- `timestamp` (int): Unix timestamp
- `comment` (str): Edit summary
- `bot` (bool): Whether editor is a bot
- `minor` (bool): Whether this is a minor edit
- `patrolled` (bool | None): Patrol status
- `revision` (dict): Old and new revision IDs
- `length` (dict): Length of old and new revisions
- `namespace` (int): Namespace ID
- `server_name` (str): Server name
- `server_url` (str): Server URL
- `wiki` (str): Wiki identifier

## models/data/rest_api/v1/entitybase/response/health.py

### HealthCheckResponse

Detailed response model for health check.

**Fields**:

- `status` (str): Overall health status
- `s3` (str): S3 service health status. Example: 'healthy'.
- `vitess` (str): Vitess service health status. Example: 'healthy'.
- `timestamp` (str): Timestamp of health check

### HealthResponse

Response model for health check.

**Fields**:

- `status` (str): Health status

### WorkerHealthCheckResponse

Model for worker health check response.

**Fields**:

- `status` (str): Health status: healthy or unhealthy
- `worker_id` (str): Unique worker identifier
- `range_status` (dict[str, Any]): Current ID range allocation status

## models/data/rest_api/v1/entitybase/response/id_response.py

### IdResponse

Response model for generated entity ID.

**Fields**:

- `id` (str): The generated entity ID (e.g., 'Q123', 'P456')

## models/data/rest_api/v1/entitybase/response/lexemes.py

### FormRepresentationResponse

**Fields**:

- `value` (str): No description

### FormRepresentationsResponse

**Fields**:

- `representations` (Dict[str, RepresentationData]): No description

### FormResponse

**Fields**:

- `id` (str): No description
- `representations` (Dict[str, RepresentationData]): No description
- `grammatical_features` (List[str]): No description
- `claims` (Dict[str, List[Dict[str, Any]]]): No description

### FormsResponse

**Fields**:

- `forms` (List[FormResponse]): No description

### RepresentationData

**Fields**:

- `language` (str): No description
- `value` (str): No description

### SenseGlossResponse

**Fields**:

- `value` (str): No description

### SenseGlossesResponse

**Fields**:

- `glosses` (Dict[str, RepresentationData]): No description

### SenseResponse

**Fields**:

- `id` (str): No description
- `glosses` (Dict[str, RepresentationData]): No description
- `claims` (Dict[str, List[Dict[str, Any]]]): No description

### SensesResponse

**Fields**:

- `senses` (List[SenseResponse]): No description

## models/data/rest_api/v1/entitybase/response/listings.py

### EntityListing

Model for entity listing entries.

**Fields**:

- `entity_id` (str): Entity ID
- `entity_type` (str): Entity type (Q, P, etc.)
- `reason` (str): Reason for listing

## models/data/rest_api/v1/entitybase/response/misc.py

### AliasesResponse

Response model for entity aliases.

**Fields**:

- `aliases` (list[str]): List of alias texts for the specified language

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

### EntityJsonResponse

Response model for JSON format entity data.

**Fields**:

- `data` (Dict[str, Any]): Entity data in JSON format

### GeneralStatsResponse

API response for general wiki statistics.

**Fields**:

- `date` (str): Date of statistics computation.
- `total_statements` (int): Total number of statements.
- `total_qualifiers` (int): Total number of qualifiers.
- `total_references` (int): Total number of references.
- `total_items` (int): Total number of items.
- `total_lexemes` (int): Total number of lexemes.
- `total_properties` (int): Total number of properties.
- `total_sitelinks` (int): Total number of sitelinks.
- `total_terms` (int): Total number of terms (labels + descriptions + aliases).
- `terms_per_language` (TermsPerLanguage): Terms count per language.
- `terms_by_type` (TermsByType): Terms count by type (labels, descriptions, aliases).

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

### MetadataData

Model for metadata data content.

**Fields**:

- `data` (str | dict[str, Any]): Metadata content as text or structured data

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

### RevisionMetadataResponse

Metadata for entity revisions.

**Fields**:

- `revision_id` (int): Revision ID
- `created_at` (str): Creation timestamp
- `user_id` (int): User ID
- `edit_summary` (str): Edit summary

### SitelinksResponse

Response model for all entity sitelinks.

**Fields**:

- `sitelinks` (dict[str, str]): Sitelinks per site

### TermsByType

Model for terms count by type.

**Fields**:

- `counts` (dict[str, int]): Type to count mapping.

### TermsPerLanguage

Model for terms count per language.

**Fields**:

- `terms` (dict[str, int]): Language to count mapping.

### TermsResponse

Model for batch terms result.

**Fields**:

- `terms` (dict[int, tuple[str, str]]): Terms by hash

### TopEntityByBacklinks

Model for entity backlink ranking.

**Fields**:

- `entity_id` (str): Entity ID
- `backlink_count` (int): Number of backlinks to this entity

### TurtleResponse

Response model for Turtle format entity data.

**Fields**:

- `turtle` (str): Entity data in Turtle format

### WatchCounts

Model for user watch counts.

**Fields**:

- `entity_count` (int): Number of entities watched
- `property_count` (int): Number of properties watched

## models/data/rest_api/v1/entitybase/response/misc2.py

### GeneralStatsData

Container for computed general wiki statistics.

**Fields**:

- `total_statements` (int): Total number of statements.
- `total_qualifiers` (int): Total number of qualifiers.
- `total_references` (int): Total number of references.
- `total_items` (int): Total number of items.
- `total_lexemes` (int): Total number of lexemes.
- `total_properties` (int): Total number of properties.
- `total_sitelinks` (int): Total number of sitelinks.
- `total_terms` (int): Total number of terms (labels + descriptions + aliases).
- `terms_per_language` (TermsPerLanguage): Terms count per language.
- `terms_by_type` (TermsByType): Terms count by type (labels, descriptions, aliases).

### QualifierResponse

Response model for qualifier data.

**Fields**:

- `qualifier` (Dict[str, Any]): Full qualifier JSON object with reconstructed snaks. Values may be int, str, dict, or list containing reconstructed snaks.
- `content_hash` (int): Hash of the qualifier content. Example: 123456789.
- `created_at` (str): Timestamp when qualifier was created. Example: '2023-01-01T12:00:00Z'.

### ReconstructedSnakValue

Response model for reconstructed snak value from hash.

**Fields**:

- `snaktype` (str): Type of snak. Example: 'value', 'novalue', 'somevalue'.
- `property` (str): Property ID. Example: 'P31'.
- `datatype` (str | None): Datatype of the snak. Example: 'wikibase-item'.
- `datavalue` (Dict[str, Any] | None): Data value of the snak. Example: {'value': 'Q1', 'type': 'wikibase-entityid'}.

### ReferenceResponse

Response model for reference data.

**Fields**:

- `reference` (Dict[str, Any]): Full reference JSON object. Example: {'snaks': {'P854': [{'value': 'https://example.com'}]}}.
- `content_hash` (int): Hash of the reference content. Example: 123456789.
- `created_at` (str): Timestamp when reference was created. Example: '2023-01-01T12:00:00Z'.

### SerializableQualifierValue

Serializable form of qualifier values for JSON serialization.

**Fields**:

- `value` (Dict[str, Any] | int | str | list['SerializableQualifierValue'] | None): Serializable qualifier value (dict, int, str, or list of SerializableQualifierValue).

### SnakResponse

Response model for snak data.

**Fields**:

- `snak` (Dict[str, Any]): Full snak JSON object. Example: {'snaktype': 'value', 'property': 'P31', 'datatype': 'wikibase-item', 'datavalue': {...}}.
- `content_hash` (int): Hash of the snak content. Example: 123456789.
- `created_at` (str): Timestamp when snak was created. Example: '2023-01-01T12:00:00Z'.

## models/data/rest_api/v1/entitybase/response/rdf.py

### DeduplicationStatsResponse

Model for deduplication cache statistics.

**Fields**:

- `hits` (int): Number of cache hits
- `misses` (int): Number of cache misses
- `size` (int): Current cache size
- `collision_rate` (float): Collision rate percentage

### FullRevisionResponse

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

### WikibasePredicatesResponse

Model for Wikibase predicate URIs for a property.

**Fields**:

- `direct` (str): Direct property predicate
- `statement` (str): Statement property predicate
- `statement_value` (str): Statement value property predicate
- `qualifier` (str): Qualifier property predicate
- `reference` (str): Reference property predicate
- `statement_value_node` (str): Statement value node predicate

## models/data/rest_api/v1/entitybase/response/result.py

### RevisionIdResult

Model for operations that return a revision ID.

**Fields**:

- `revision_id` (int): The revision ID of the created/updated entity, or 0 for idempotent operations

### RevisionResult

Result of revision processing.

**Fields**:

- `success` (bool): Whether the revision processing was successful
- `revision_id` (int): The ID of the created or updated revision
- `error` (str): Error message if the operation failed

## models/data/rest_api/v1/entitybase/response/statement.py

### MostUsedStatementsResponse

**Fields**:

- `statements` (list[int]): List of statement hashes sorted by ref_count DESC

### PropertyCountsResponse

**Fields**:

- `property_counts` (dict[str, int]): Dict mapping property ID -> statement count

### PropertyHashesResponse

**Fields**:

- `property_hashes` (list[int]): List of statement hashes for specified properties

### PropertyListResponse

**Fields**:

- `properties` (list[str]): List of unique property IDs

### PropertyRecalculationResult

Result of property count recalculation after statement removal.

**Fields**:

- `properties` (list[str]): List of property IDs after recalculation
- `property_counts` (PropertyCounts): Mapping of property ID to statement count after recalculation

### StatementBatchResponse

Response model for batch statement queries.

**Fields**:

- `statements` (list[StatementResponse]): List of statements
- `not_found` (list[int]): Hashes that were not found

### StatementHashResult

**Fields**:

- `statements` (list[int]): List of statement hashes (rapidhash of each statement). Example: [123456789, 987654321].
- `properties` (list[str]): Sorted list of unique property IDs. Example: ['P31', 'P279'].
- `property_counts` (PropertyCounts): Dict mapping property ID to count of statements. Example: {'P31': 5}.
- `full_statements` (list[Dict[str, Any]]): List of full statement dicts (parallel with hashes). Example: [{'id': 'P31', 'value': 'Q5'}].

### StatementResponse

Response model for statement data.

**Fields**:

- `schema_version` (str): Schema version for the statement. Example: '1.0'.
- `content_hash` (int): Hash of the statement content. Example: 123456789.
- `statement` (Dict[str, Any]): Full statement JSON object. Example: {'id': 'P31', 'value': 'Q5'}.
- `created_at` (str): Timestamp when statement was created. Example: '2023-01-01T12:00:00Z'.

### StatementsHashResponse

Response model for entity statement hashes (schema 2.0.0).

**Fields**:

- `property_hashes` (list[int]): List of statement hashes (rapidhash of each statement). Example: [123456789, 987654321].

### StatementsResponse

Response model for statements.

**Fields**:

- `statements` (dict[str, Any]): Statements data

## models/data/rest_api/v1/entitybase/response/thanks.py

### ThankItemResponse

Individual thank item.

**Fields**:

- `id` (int): Unique identifier for the thank
- `from_user_id` (int): User ID who sent the thank
- `to_user_id` (int): User ID who received the thank
- `entity_id` (str): Entity ID associated with the thank
- `revision_id` (int): Revision ID associated with the thank
- `created_at` (datetime): Timestamp when the thank was created

### ThankResponse

Response for sending a thank.

**Fields**:

- `thank_id` (int): Thank ID
- `from_user_id` (int): User ID sending the thank
- `to_user_id` (int): User ID receiving the thank
- `entity_id` (str): Entity ID
- `revision_id` (int): Revision ID
- `created_at` (str): Creation timestamp

### ThanksListResponse

Response for thanks list queries.

**Fields**:

- `user_id` (int): User ID
- `thanks` (List['ThankItemResponse']): List of thanks
- `total_count` (int): Total count of thanks
- `has_more` (bool): Whether there are more thanks available

## models/data/rest_api/v1/entitybase/response/user.py

### MessageResponse

Generic message response.

**Fields**:

- `message` (str): No description

### NotificationResponse

Response for user notifications.

**Fields**:

- `user_id` (int): No description
- `notifications` (list): No description

### UserCreateResponse

Response for user creation.

**Fields**:

- `user_id` (int): No description
- `created` (bool): No description

### UserResponse

User model.
    We intentionally don't have auth, nor store the usernames.

**Fields**:

- `user_id` (int): No description
- `created_at` (datetime): No description
- `preferences` (dict | None): No description

### WatchlistToggleResponse

Response for watchlist toggle.

**Fields**:

- `user_id` (int): No description
- `enabled` (bool): No description

## models/data/rest_api/v1/entitybase/response/user_activity.py

### UserActivityItemResponse

Individual user activity item.

**Fields**:

- `id` (int): Unique identifier for the activity
- `user_id` (int): User ID who performed the activity
- `activity_type` (UserActivityType): Type of activity performed
- `entity_id` (str): Entity ID associated with the activity
- `revision_id` (int): Revision ID associated with the activity
- `created_at` (datetime): Timestamp when the activity occurred

### UserActivityResponse

Response for user activity query.

**Fields**:

- `user_id` (int): User ID
- `activities` (List[UserActivityItemResponse]): List of user activities

## models/data/rest_api/v1/entitybase/response/user_preferences.py

### UserPreferencesResponse

Response for user preferences query.

**Fields**:

- `user_id` (int): User ID
- `notification_limit` (int): Notification limit
- `retention_hours` (int): Retention hours

## models/data/rest_api/v1/entitybase/response/user_stats.py

### UserStatsData

Container for computed user statistics.

**Fields**:

- `total_users` (int): Total number of users. Example: 1000.
- `active_users` (int): Number of active users. Example: 500.

### UserStatsResponse

API response for user statistics.

**Fields**:

- `date` (str): Date of statistics computation. Example: '2023-01-01'.
- `total_users` (int): Total number of users. Example: 1000.
- `active_users` (int): Number of active users. Example: 500.

## models/data/rest_api/v1/entitybase/response/watchlist.py

### WatchlistEntryResponse

Watchlist entry for database.

**Fields**:

- `id` (int): Unique identifier for the watchlist entry
- `user_id` (int): User ID who owns the watchlist entry
- `internal_entity_id` (int): Internal entity ID being watched
- `watched_properties` (List[str] | None): List of specific properties being watched, null for all

### WatchlistResponse

Response for listing user's watchlist.

**Fields**:

- `user_id` (int): User ID for whom the watchlist is returned
- `watches` (List[dict]): List of watchlist entries with entity_id and properties

