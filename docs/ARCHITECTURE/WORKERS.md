# Workers Overview

## Backlink Statistics Worker

**Class**: `BacklinkStatisticsWorker`
**Location**: `models/workers/backlink_statistics/backlink_statistics_worker.py`
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

## Entity Diff Worker

**Class**: ``
**Location**: `models/workers/entity_diff/rdf_serializer.py`
**Purpose**: 

**Health Checks**: Available via worker health endpoint

## General Stats Worker

**Class**: `GeneralStatsWorker`
**Location**: `models/workers/general_stats/general_stats_worker.py`
**Purpose**: 

**Health Checks**: Available via worker health endpoint

## Id Generation Worker

**Class**: `IdGeneratorWorker`
**Location**: `models/workers/id_generation/id_generation_worker.py`
**Purpose**: Asynchronous worker service for generating Wikibase entity IDs using range-based allocation. This worker reserves blocks (ranges) of IDs from the database to minimize contention during high-volume entity creation. It monitors range status, handles graceful shutdown, and provides health checks for monitoring. The worker initializes Vitess and Enumeration services, then runs a continuous loop checking ID range availability. IDs are allocated from pre-reserved ranges to ensure efficient, low-latency ID generation.

**Configuration**:
- `WORKER_ID`: Unique worker identifier (default: auto-generated)

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

