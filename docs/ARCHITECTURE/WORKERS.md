# Workers Overview

## Backlink Statistics Worker

**Class**: `BacklinkStatisticsWorker`
**Location**: `models/workers/backlink_statistics/backlink_statistics_worker.py`
**Purpose**: Computes and stores backlink statistics for entities. Runs daily to analyze which entities reference other entities and stores aggregate statistics.

**Configuration**:
- `backlink_stats_enabled`: True
- `backlink_stats_schedule`: "0 2 * * *"  # Daily at 2 AM
- `backlink_stats_top_limit`: 100

**Health Checks**: Available via worker health endpoint

---

## Create Worker

**Class**: ``
**Location**: `models/workers/create/__main__.py`
**Purpose**: Initializes S3 buckets required for entity storage. Runs once at deployment to ensure all required buckets exist.

**Health Checks**: Available via worker health endpoint

---

## Elasticsearch Indexer Worker

**Class**: `ElasticsearchIndexerWorker`
**Location**: `models/workers/elasticsearch_indexer/elasticsearch_indexer_worker.py`
**Purpose**: Consumes entity change events from Kafka and indexes them to Elasticsearch. Transforms entity data into searchable documents for full-text search.

**Configuration**:
- `elasticsearch_enabled`: True/False
- `elasticsearch_host`: Elasticsearch host
- `elasticsearch_port`: Elasticsearch port
- `kafka_bootstrap_servers`: Kafka brokers

**Health Checks**: Available via worker health endpoint

## Entity Diff Worker

**Class**: `EntityDiffWorker`
**Location**: `models/workers/entity_diff/entity_diff_worker.py`
**Purpose**: Computes diffs between RDF versions of Wikibase entities. Converts entity data to RDF canonical form and generates change events for downstream processing.

**Health Checks**: Available via worker health endpoint

---

## General Stats Worker

**Class**: `GeneralStatsWorker`
**Location**: `models/workers/general_stats/general_stats_worker.py`
**Purpose**: Computes and stores general wiki statistics including total entities, statements, terms, and itemized counts by type. Runs daily on schedule.

**Configuration**:
- `general_stats_enabled`: True
- `general_stats_schedule`: Schedule string

**Health Checks**: Available via worker health endpoint

## Id Generation Worker

**Class**: `IdGeneratorWorker`
**Location**: `models/workers/id_generation/id_generation_worker.py`
**Purpose**: Asynchronous worker service for generating Wikibase entity IDs using range-based allocation. This worker reserves blocks (ranges) of IDs from the database to minimize contention during high-volume entity creation. It monitors range status, handles graceful shutdown, and provides health checks for monitoring. The worker initializes Vitess and Enumeration services, then runs a continuous loop checking ID range availability. IDs are allocated from pre-reserved ranges to ensure efficient, low-latency ID generation.

**Configuration**:
- `WORKER_ID`: Unique worker identifier (default: auto-generated)

**Health Checks**: Available via worker health endpoint

## Incremental Rdf Worker

**Class**: `IncrementalRDFWorker`
**Location**: `models/workers/incremental_rdf/incremental_rdf_worker.py`
**Purpose**: Consumes entity change events from Kafka and generates incremental RDF diffs. Produces RDF change events for downstream consumers like the RDF dumps worker.

**Configuration**:
- `streaming_enabled`: True
- `kafka_bootstrap_servers`: Kafka brokers
- `kafka_entity_diff_topic`: Topic for diff events

**Health Checks**: Available via worker health endpoint

---

## Json Dumps Worker

**Class**: `JsonDumpWorker`
**Location**: `models/workers/json_dumps/json_dump_worker.py`
**Purpose**: Generates JSON dumps of all entity data. Exports complete entity data in JSON format to S3 on a scheduled basis for backup and external consumption.

**Configuration**:
- `json_dump_enabled`: True
- `json_dump_schedule`: "0 3 * * *"  # Daily at 3 AM
- `json_dump_batch_size`: 1000

**Health Checks**: Available via worker health endpoint

---

## Meilisearch Indexer Worker

**Class**: `MeilisearchIndexerWorker`
**Location**: `models/workers/meilisearch_indexer/meilisearch_indexer_worker.py`
**Purpose**: Consumes entity change events from Kafka and indexes them to Meilisearch. Alternative search backend to Elasticsearch with different performance characteristics.

**Configuration**:
- `meilisearch_enabled`: True/False
- `meilisearch_host`: Meilisearch host
- `meilisearch_port`: Meilisearch port
- `meilisearch_api_key`: API key (optional)
- `meilisearch_index`: Index name

**Health Checks**: Available via worker health endpoint

## Notification Cleanup Worker

**Class**: `NotificationCleanupWorker`
**Location**: `models/workers/notification_cleanup/main.py`
**Purpose**: Worker that periodically cleans up old notifications to enforce limits.

**Health Checks**: Available via worker health endpoint

## Purge Worker

**Class**: `PurgeWorker`
**Location**: `models/workers/purge/purge_worker.py`
**Purpose**: Worker that periodically purges all S3 buckets and truncates database tables.

**Health Checks**: Available via worker health endpoint

## Ttl Dumps Worker

**Class**: `TtlDumpWorker`
**Location**: `models/workers/ttl_dumps/ttl_dump_worker.py`
**Purpose**: Generates TTL (Turtle) RDF dumps of entity data. Exports complete entity data in RDF Turtle format to S3 on a scheduled basis for semantic web consumption.

**Configuration**:
- `ttl_dump_enabled`: True
- `ttl_dump_schedule`: "0 4 * * *"  # Daily at 4 AM
- `ttl_dump_batch_size`: 100

**Health Checks**: Available via worker health endpoint

---

## User Stats Worker

**Class**: `UserStatsWorker`
**Location**: `models/workers/user_stats/user_stats_worker.py`
**Purpose**: Computes and stores user activity statistics. Tracks active users, edit counts, and activity metrics on a daily schedule.

**Configuration**:
- `user_stats_enabled`: True
- `user_stats_schedule`: Schedule string

**Health Checks**: Available via worker health endpoint

## Watchlist Consumer Worker

**Class**: `WatchlistConsumerWorker`
**Location**: `models/workers/watchlist_consumer/main.py`
**Purpose**: Worker that consumes entity change events and creates notifications for watchers.

**Configuration**:
- `kafka_bootstrap_servers`: Comma-separated list of Kafka broker addresses
- `kafka_topic`: Kafka topic for entity changes (default: "wikibase-entity-changes")

**Health Checks**: Available via worker health endpoint

**Dependencies**: Requires aiokafka for Kafka consumption.

