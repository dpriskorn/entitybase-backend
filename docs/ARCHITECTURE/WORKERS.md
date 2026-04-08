# Workers Overview

## Backlink Statistics Worker

**Class**: ``
**Location**: `models/workers/backlink_statistics/__main__.py`
**Purpose**: 

**Configuration**:
- `backlink_stats_enabled`: True
- `backlink_stats_schedule`: "0 2 * * *"  # Daily at 2 AM
- `backlink_stats_top_limit`: 100

**Health Checks**: Available via worker health endpoint

## Dev Worker

**Class**: ``
**Location**: `models/workers/dev/__main__.py`
**Purpose**: 

**Health Checks**: Available via worker health endpoint

## Elasticsearch Indexer Worker

**Class**: `ElasticsearchIndexerWorker`
**Location**: `models/workers/elasticsearch_indexer/__main__.py`
**Purpose**: Worker that consumes entity change events from Kafka and indexes them to Elasticsearch. It fetches entity data from S3, transforms it using `transform_to_elasticsearch()`, and indexes the document via `ElasticsearchClient`.

**Configuration**:
- `elasticsearch_enabled`: Enable/disable the worker (default: false)
- `elasticsearch_host`: Elasticsearch host (default: "localhost")
- `elasticsearch_port`: Elasticsearch port (default: 9200)
- `elasticsearch_index`: Index name (default: "entitybase")
- `elasticsearch_consumer_group`: Kafka consumer group (default: "entitybase-elasticsearch-indexer")

**Note**: This worker calls the transformer functions directly rather than using the REST API endpoints. This is more efficient as it avoids HTTP overhead and runs in the same process.

**Health Checks**: Available via worker health endpoint

## Meilisearch Indexer Worker

**Class**: `MeilisearchIndexerWorker`
**Location**: `models/workers/meilisearch_indexer/__main__.py`
**Purpose**: Worker that consumes entity change events from Kafka and indexes them to Meilisearch. It fetches entity data from S3, transforms it using `transform_to_meilisearch()`, and indexes the document via `MeilisearchClient`.

**Configuration**:
- `meilisearch_enabled`: Enable/disable the worker (default: false)
- `meilisearch_host`: Meilisearch host (default: "localhost")
- `meilisearch_port`: Meilisearch port (default: 7700)
- `meilisearch_api_key`: API key for authentication (default: "")
- `meilisearch_index`: Index name (default: "entitybase")
- `meilisearch_consumer_group`: Kafka consumer group (default: "entitybase-meilisearch-indexer")

**Note**: This worker calls the transformer functions directly rather than using the REST API endpoints. This is more efficient as it avoids HTTP overhead and runs in the same process.

**Health Checks**: Available via worker health endpoint

## Entity Diff Worker

**Class**: ``
**Location**: `models/workers/entity_diff/rdf_serializer.py`
**Purpose**: 

**Health Checks**: Available via worker health endpoint

## General Stats Worker

**Class**: ``
**Location**: `models/workers/general_stats/__main__.py`
**Purpose**: 

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
**Purpose**: Worker that consumes entity change events and generates incremental RDF diffs. This worker: 1. Consumes entity change events from entitybase.entity_change Kafka topic 2. Looks up revision metadata in MySQL to get content hashes 3. Fetches entity snapshots from S3 for both old and new revisions 4. Computes RDF diffs using IncrementalRDFUpdater 5. Publishes RDF change events to incremental_rdf_diff Kafka topic

**Health Checks**: Available via worker health endpoint

## Json Dumps Worker

**Class**: ``
**Location**: `models/workers/json_dumps/__main__.py`
**Purpose**: 

**Health Checks**: Available via worker health endpoint

## Notification Cleanup Worker

**Class**: `NotificationCleanupWorker`
**Location**: `models/workers/notification_cleanup/main.py`
**Purpose**: Worker that periodically cleans up old notifications to enforce limits.

**Health Checks**: Available via worker health endpoint

## Ttl Dumps Worker

**Class**: ``
**Location**: `models/workers/ttl_dumps/__main__.py`
**Purpose**: 

**Health Checks**: Available via worker health endpoint

## User Stats Worker

**Class**: `UserStatsWorker`
**Location**: `models/workers/user_stats/user_stats_worker.py`
**Purpose**: 

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

