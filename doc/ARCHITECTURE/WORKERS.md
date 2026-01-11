# Workers Overview

## Backlink Statistics Worker

**Class**: `BacklinkStatisticsWorker`
**Location**: `models/workers/backlink_statistics/backlink_statistics_worker.py`
**Purpose**: Background worker for computing backlink statistics.

**Configuration**:
- `backlink_stats_enabled`: True
- `backlink_stats_schedule`: "0 2 * * *"  # Daily at 2 AM
- `backlink_stats_top_limit`: 100

**Health Checks**: Available via worker health endpoint

## Id Generation Worker

**Class**: `IdGeneratorWorker`
**Location**: `models/workers/id_generation/id_generation_worker.py`
**Purpose**: Asynchronous worker service for generating Wikibase entity IDs using range-based allocation. This worker reserves blocks (ranges) of IDs from the database to minimize contention during high-volume entity creation. It monitors range status, handles graceful shutdown, and provides health checks for monitoring. The worker initializes Vitess and Enumeration services, then runs a continuous loop checking ID range availability. IDs are allocated from pre-reserved ranges to ensure efficient, low-latency ID generation.

**Configuration**:
- `WORKER_ID`: Unique worker identifier (default: auto-generated)

**Health Checks**: Available via worker health endpoint

