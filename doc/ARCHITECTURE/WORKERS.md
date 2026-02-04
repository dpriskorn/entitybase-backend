# Workers Overview

This document describes all background workers in the Wikibase backend system.

## Table of Contents

- [ID Generation Worker](#id-generation-worker)
- [Entity Diff Worker](#entity-diff-worker)
- [Backlink Statistics Worker](#backlink-statistics-worker)
- [User Stats Worker](#user-stats-worker)
- [General Stats Worker](#general-stats-worker)
- [Watchlist Consumer Worker](#watchlist-consumer-worker)
- [Notification Cleanup Worker](#notification-cleanup-worker)
- [Dev Worker](#dev-worker)

---

## ID Generation Worker

### Overview

**Purpose**: Asynchronous worker service for generating Wikibase entity IDs using range-based allocation. This worker reserves blocks (ranges) of IDs from the database to minimize contention during high-volume entity creation.

**Class**: `IdGeneratorWorker`
**Location**: `src/models/workers/id_generation/id_generation_worker.py`
**Schedule**: Continuous (no cron schedule - runs continuously)

### Architecture

The ID generation system uses a **range-based allocation** strategy:

1. **Worker polls id_ranges table** for entities approaching range exhaustion
2. **Reserves new range** by updating `current_range_start` and `current_range_end`
3. **Provides IDs** via EnumerationService with atomic increment
4. **Health checks** monitor worker status

### Database Schema

```sql
CREATE TABLE id_ranges (
    entity_type VARCHAR(50) PRIMARY KEY,
    current_range_start BIGINT UNSIGNED NOT NULL,
    current_range_end BIGINT UNSIGNED NOT NULL,
    next_id BIGINT UNSIGNED NOT NULL,
    range_size BIGINT UNSIGNED NOT NULL DEFAULT 1000,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### Worker Logic

**Initialization**:
```python
# Initialize entity types with initial ranges
INSERT INTO id_ranges (entity_type, current_range_start, current_range_end, next_id, range_size)
VALUES
    ('item', 1, 1000, 1, 1000),
    ('property', 1, 1000, 1, 1000),
    ('lexeme', 1, 1000, 1, 1000),
    ('entityschema', 1, 1000, 1, 1000);
```

**Continuous Loop**:
```python
while running:
    # Check each entity type
    for entity_type in ['item', 'property', 'lexeme', 'entityschema']:
        # Query id_ranges table
        range_data = query_id_range(entity_type)

        # If next_id >= current_range_end (90% threshold), reserve new range
        if range_data.next_id >= range_data.current_range_end * 0.9:
            reserve_new_range(entity_type, range_data.current_range_end)

    # Sleep for polling interval
    sleep(1)
```

**Range Reservation**:
```sql
UPDATE id_ranges
SET current_range_start = current_range_end + 1,
    current_range_end = current_range_end + range_size,
    next_id = current_range_start + 1
WHERE entity_type = ? AND next_id = ?
```

### EnumerationService

The `EnumerationService` provides thread-safe ID allocation for API handlers:

```python
class EnumerationService:
    def __init__(self, vitess_client):
        self.vitess_client = vitess_client
        self.cache = {}  # In-memory cache for performance

    def allocate_id(self, entity_type: EntityType) -> str:
        """Allocate the next available ID for an entity type."""
        # Check cache
        if entity_type in self.cache and self.cache[entity_type]:
            return self.cache[entity_type].pop()

        # Fetch from database
        next_id = self.vitess_client.get_next_id(entity_type)

        # Format with prefix
        if entity_type == EntityType.ITEM:
            return f"Q{next_id}"
        elif entity_type == EntityType.PROPERTY:
            return f"P{next_id}"
        elif entity_type == EntityType.LEXEME:
            return f"L{next_id}"
        elif entity_type == EntityType.ENTITYSCHEMA:
            return f"E{next_id}"
```

### Configuration

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `WORKER_ID` | str | Auto-generated | Unique worker identifier |

### Health Checks

Health endpoint provides:
- Worker status (running/stopped)
- Last range reservation time
- Current ID ranges for each entity type
- Cache statistics

### Benefits

- **High Throughput**: Pre-allocated ranges enable thousands of IDs per second
- **Low Latency**: In-memory caching eliminates database round-trips
- **Fault Tolerant**: Multiple workers can run simultaneously with CAS (Compare-And-Swap) operations
- **Scalable**: Range size can be adjusted based on load

---

## Entity Diff Worker

### Overview

**Purpose**: Computes RDF diffs between entity revisions and streams changes to Kafka for downstream consumers (e.g., SPARQL update, change notifications).

**Class**: `EntityDiffWorker`
**Location**: `src/models/workers/entity_diff/entity_diff_worker.py`
**Schedule**: Polling-based (continuous or configurable interval)

### Architecture

The worker processes entity revisions in order:

1. **Polls entity_head** for updated entities
2. **Fetches revisions** from S3
3. **Generates RDF** for each revision
4. **Computes diffs** between consecutive revisions
5. **Streams changes** to Kafka topic

### RDF Canonicalization

Uses **URDNA2015** algorithm for consistent blank node handling:

```python
from rdflib import Graph
from rdflib.compare import isomorphic

def canonicalize_rdf(turtle_data: str) -> str:
    graph = Graph()
    graph.parse(data=turtle_data, format="turtle")

    # Canonicalize blank nodes
    canonical = graph.serialize(format="turtle", canonicalize=True)
    return canonical
```

### Diff Computation

Compares RDF triples between revisions:

```python
def compute_rdf_diff(old_rdf: str, new_rdf: str) -> RDFDiff:
    old_graph = Graph().parse(data=old_rdf, format="turtle")
    new_graph = Graph().parse(data=new_rdf, format="turtle")

    # Compute added triples
    added = new_graph - old_graph

    # Compute removed triples
    removed = old_graph - new_graph

    return RDFDiff(added=added, removed=removed)
```

### Kafka Streaming

Publishes diff events to `wikibase.entity_diff` topic:

```json
{
  "schema_version": "2.0.0",
  "entity_id": "Q123",
  "revision_id": 42,
  "previous_revision_id": 41,
  "rdf_added_data": "<turtle_format>",
  "rdf_removed_data": "<turtle_format>",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### Configuration

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `entity_diff_enabled` | bool | True | Enable entity diff worker |
| `entity_diff_poll_interval` | int | 60 | Poll interval in seconds |
| `kafka_brokers` | str | - | Kafka broker addresses |
| `kafka_entity_diff_topic` | str | "wikibase.entity_diff" | Kafka topic for entity diffs |
| `streaming_entity_diff_version` | str | "2.0.0" | Entity diff event schema version |

### Supported RDF Formats

- **Turtle** (default): Human-readable RDF format
- **RDF XML**: XML-based RDF format
- **NTriples**: Line-based triple format

### Health Checks

Health endpoint provides:
- Worker status (running/stopped)
- Last processed entity
- Number of diffs computed
- Kafka publishing statistics
- Processing latency metrics

---

## Backlink Statistics Worker

### Overview

**Purpose**: Computes backlink statistics for entities, tracking how many entities reference each entity via statements. Used for ranking and analytics.

**Class**: `BacklinkStatisticsWorker`
**Location**: `src/models/workers/backlink_statistics/backlink_statistics_worker.py`
**Schedule**: Daily at 2 AM (`0 2 * * *`)

### Architecture

1. **Queries entity_backlinks** table
2. **Aggregates backlink counts** per entity
3. **Updates backlink_statistics** table
4. **Computes top N entities** by backlink count

### Database Schema

**Backlink Statistics**:
```sql
CREATE TABLE backlink_statistics (
    entity_id VARCHAR(50) PRIMARY KEY,
    backlink_count INT UNSIGNED NOT NULL,
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_backlink_count (backlink_count DESC)
);
```

**Entity Backlinks**:
```sql
CREATE TABLE entity_backlinks (
    entity_id VARCHAR(50) NOT NULL,
    backlink_id VARCHAR(50) NOT NULL,
    property_id VARCHAR(50) NOT NULL,
    added_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (entity_id, backlink_id, property_id),
    INDEX idx_backlink (backlink_id, property_id)
);
```

### Computation Logic

```python
def compute_backlink_statistics():
    # Aggregate backlink counts from entity_backlinks
    query = """
        INSERT INTO backlink_statistics (entity_id, backlink_count)
        SELECT backlink_id, COUNT(*) as count
        FROM entity_backlinks
        GROUP BY backlink_id
        ON DUPLICATE KEY UPDATE
            backlink_count = VALUES(backlink_count),
            last_updated = CURRENT_TIMESTAMP
    """
    execute(query)

    # Clean up deleted entities (count = 0)
    execute("DELETE FROM backlink_statistics WHERE backlink_count = 0")
```

### Configuration

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `backlink_stats_enabled` | bool | True | Enable backlink statistics worker |
| `backlink_stats_schedule` | str | "0 2 * * *" | Cron schedule (daily at 2 AM) |
| `backlink_stats_top_limit` | int | 100 | Number of top entities to track |

### Health Checks

Health endpoint provides:
- Worker status (running/stopped)
- Last run timestamp
- Number of entities processed
- Top N backlinked entities

---

## User Stats Worker

### Overview

**Purpose**: Computes daily user statistics including total users and active users (users with activity in last 30 days). Results stored in `user_daily_stats` table for fast API retrieval.

**Class**: `UserStatsWorker`
**Location**: `src/models/workers/user_stats/user_stats_worker.py`
**Schedule**: Daily at 2 AM (`0 2 * * *`)

### Architecture

1. **Queries users table** for all users
2. **Counts active users** (last_activity within 30 days)
3. **Stores daily stats** in `user_daily_stats` table
4. **Provides fallback** to live computation if stats not available

### Database Schema

```sql
CREATE TABLE user_daily_stats (
    stat_date DATE PRIMARY KEY,
    total_users BIGINT UNSIGNED NOT NULL,
    active_users BIGINT UNSIGNED NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    id INT UNSIGNED PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### Computation Logic

```python
def compute_user_statistics():
    today = datetime.now().date()

    # Count total users
    total_users = query("SELECT COUNT(*) FROM users")

    # Count active users (last activity in last 30 days)
    active_users = query("""
        SELECT COUNT(*) FROM users
        WHERE last_activity >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
    """)

    # Insert daily stats
    execute("""
        INSERT INTO user_daily_stats (stat_date, total_users, active_users)
        VALUES (?, ?, ?)
        ON DUPLICATE KEY UPDATE
            total_users = VALUES(total_users),
            active_users = VALUES(active_users)
    """, today, total_users, active_users)
```

### API Integration

Stats served via `/users/stat` endpoint:

```python
GET /users/stat

Response:
{
  "stat_date": "2025-01-15",
  "total_users": 12345,
  "active_users": 8765
}
```

### Configuration

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `user_stats_enabled` | bool | True | Enable user stats worker |
| `user_stats_schedule` | str | "0 2 * * *" | Cron schedule (daily at 2 AM) |

### Health Checks

Health endpoint provides:
- Worker status (running/stopped)
- Last run timestamp
- Current statistics
- Live vs. stored stats comparison

---

## General Stats Worker

### Overview

**Purpose**: Computes daily general wiki statistics including statements, qualifiers, references, entities, sitelinks, and term breakdowns. Results stored in `general_daily_stats` table for fast API retrieval.

**Class**: `GeneralStatsWorker`
**Location**: `src/models/workers/general_stats/general_stats_worker.py`
**Schedule**: Daily at 2 AM (`0 2 * * *`)

### Architecture

1. **Queries all tables** for counts
2. **Computes term breakdowns** by language and type
3. **Stores daily stats** in `general_daily_stats` table
4. **Provides fallback** to live computation if stats not available

### Database Schema

```sql
CREATE TABLE general_daily_stats (
    stat_date DATE PRIMARY KEY,
    total_statements BIGINT UNSIGNED NOT NULL,
    total_qualifiers BIGINT UNSIGNED NOT NULL,
    total_references BIGINT UNSIGNED NOT NULL,
    total_items BIGINT UNSIGNED NOT NULL,
    total_lexemes BIGINT UNSIGNED NOT NULL,
    total_properties BIGINT UNSIGNED NOT NULL,
    total_sitelinks BIGINT UNSIGNED NOT NULL,
    total_terms BIGINT UNSIGNED NOT NULL,
    terms_per_language JSON,
    terms_by_type JSON,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Computation Logic

```python
def compute_general_statistics():
    today = datetime.now().date()

    # Count statements
    total_statements = query("SELECT COUNT(*) FROM statement_content")

    # Count qualifiers, references (from S3 or Vitess)
    total_qualifiers = query("SELECT SUM(ref_count) FROM qualifiers")
    total_references = query("SELECT SUM(ref_count) FROM references")

    # Count entities by type
    total_items = query("SELECT COUNT(*) FROM entity_head WHERE entity_id LIKE 'Q%'")
    total_lexemes = query("SELECT COUNT(*) FROM entity_head WHERE entity_id LIKE 'L%'")
    total_properties = query("SELECT COUNT(*) FROM entity_head WHERE entity_id LIKE 'P%'")

    # Count sitelinks (approximate from entity_revisions)
    total_sitelinks = query("SELECT COUNT(DISTINCT sitelink_id) FROM entity_revisions")

    # Count terms (labels + descriptions + aliases)
    total_terms = count_terms()

    # Compute breakdowns
    terms_per_language = compute_terms_by_language()
    terms_by_type = compute_terms_by_type()

    # Insert daily stats
    execute("""
        INSERT INTO general_daily_stats
        (stat_date, total_statements, total_qualifiers, total_references,
         total_items, total_lexemes, total_properties, total_sitelinks,
         total_terms, terms_per_language, terms_by_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON DUPLICATE KEY UPDATE ...
    """, ...)
```

### API Integration

Stats served via `/stats` endpoint:

```python
GET /stats

Response:
{
  "stat_date": "2025-01-15",
  "total_statements": 12345678,
  "total_qualifiers": 8765432,
  "total_references": 5432109,
  "total_items": 9876543,
  "total_lexemes": 123456,
  "total_properties": 76543,
  "total_sitelinks": 6543210,
  "total_terms": 23456789,
  "terms_per_language": {
    "en": 1234567,
    "de": 987654,
    ...
  },
  "terms_by_type": {
    "labels": 8765432,
    "descriptions": 7654321,
    "aliases": 7067036
  }
}
```

### Configuration

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `general_stats_enabled` | bool | True | Enable general stats worker |
| `general_stats_schedule` | str | "0 2 * * *" | Cron schedule (daily at 2 AM) |

### Health Checks

Health endpoint provides:
- Worker status (running/stopped)
- Last run timestamp
- Current statistics
- Computation duration

---

## Watchlist Consumer Worker

### Overview

**Purpose**: Consumes entity change events from Kafka and creates notifications for users watching those entities. Enables real-time change notifications for watchlist features.

**Class**: `WatchlistConsumerWorker`
**Location**: `src/models/workers/watchlist_consumer/main.py`
**Schedule**: Continuous (runs continuously consuming events)

### Architecture

1. **Subscribes to Kafka topic** `entitybase.entity_change`
2. **Consumes change events** (entity_id, revision_id, change_type)
3. **Queries watchlist** for users watching entity
4. **Creates notifications** in `watchlist_notifications` table
5. **Updates last_notification_at** in watchlist

### Database Schema

**Watchlist**:
```sql
CREATE TABLE user_watchlist (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    user_id INT UNSIGNED NOT NULL,
    entity_id VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_notification_at TIMESTAMP NULL,
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    watched_properties TEXT NOT NULL DEFAULT '',
    UNIQUE KEY uk_watch (user_id, entity_id),
    INDEX idx_user_entity (user_id, entity_id),
    INDEX idx_last_notification (last_notification_at)
);
```

**Watchlist Notifications**:
```sql
CREATE TABLE watchlist_notifications (
    id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
    user_id INT UNSIGNED NOT NULL,
    entity_id VARCHAR(50) NOT NULL,
    revision_id BIGINT UNSIGNED NOT NULL,
    change_type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_checked BOOLEAN NOT NULL DEFAULT FALSE,
    INDEX idx_user (user_id, created_at, is_checked),
    INDEX idx_entity (entity_id, created_at)
);
```

### Kafka Event Schema

**Entity Change Event**:
```json
{
  "schema_version": "1.0.0",
  "entity_id": "Q123",
  "revision_id": 42,
  "operation": "create|update|delete",
  "editor_id": 123,
  "edit_summary": "Updated description",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### Consumer Logic

```python
async def consume_entity_changes():
    consumer = KafkaConsumer(
        bootstrap_servers=settings.kafka_brokers,
        topic="entitybase.entity_change",
        group_id="watchlist-consumer"
    )

    async for message in consumer:
        event = EntityChangeEvent.parse_raw(message.value)

        # Find users watching this entity
        watchers = query("""
            SELECT user_id, watched_properties FROM user_watchlist
            WHERE entity_id = ? AND is_enabled = TRUE
        """, event.entity_id)

        # Create notifications for each watcher
        for watcher in watchers:
            insert_notification(
                user_id=watcher.user_id,
                entity_id=event.entity_id,
                revision_id=event.revision_id,
                change_type=event.operation
            )

            # Update last_notification_at
            execute("""
                UPDATE user_watchlist
                SET last_notification_at = CURRENT_TIMESTAMP
                WHERE user_id = ? AND entity_id = ?
            """, watcher.user_id, event.entity_id)
```

### Configuration

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `kafka_brokers` | str | - | Kafka broker addresses |
| `kafka_entitychange_json_topic` | str | "entitybase.entity_change" | Kafka topic for entity changes |
| `watchlist_consumer_enabled` | bool | True | Enable watchlist consumer worker |

### Health Checks

Health endpoint provides:
- Worker status (running/stopped)
- Kafka consumer lag (messages behind)
- Number of notifications created
- Last processed event timestamp

---

## Notification Cleanup Worker

### Overview

**Purpose**: Periodically cleans up old watchlist notifications to enforce retention limits and prevent database bloat.

**Class**: `NotificationCleanupWorker`
**Location**: `src/models/workers/notification_cleanup/main.py`
**Schedule**: Configurable (e.g., daily at 3 AM)

### Architecture

1. **Queries watchlist_notifications** for old notifications
2. **Deletes notifications** older than retention period
3. **Updates notification counts** for watchlist entries
4. **Reports cleanup statistics**

### Cleanup Logic

```python
def cleanup_old_notifications(retention_days=30):
    cutoff_date = datetime.now() - timedelta(days=retention_days)

    # Delete old notifications
    deleted_count = execute("""
        DELETE FROM watchlist_notifications
        WHERE created_at < ? AND is_checked = TRUE
    """, cutoff_date)

    logger.info(f"Deleted {deleted_count} old notifications")
```

### Configuration

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `notification_cleanup_enabled` | bool | True | Enable notification cleanup worker |
| `notification_cleanup_schedule` | str | "0 3 * * *" | Cron schedule (daily at 3 AM) |
| `notification_retention_days` | int | 30 | Retention period for notifications |

### Health Checks

Health endpoint provides:
- Worker status (running/stopped)
- Last cleanup timestamp
- Number of notifications deleted
- Current notification count

---

## Dev Worker

### Overview

**Purpose**: Development tools for creating S3 buckets and database tables. Used during initial setup and development.

**Class**: DevWorker (multiple command handlers)
**Location**: `src/models/workers/dev/__main__.py`
**Schedule**: On-demand (manual execution)

### Available Commands

#### Create Buckets

Creates all required S3 buckets:

```bash
python -m models.workers.dev create_buckets
```

**Buckets Created**:
- `s3_revisions_bucket` (default: "revisions")
- `s3_statements_bucket` (default: "statements")
- `s3_references_bucket` (default: "references")
- `s3_qualifiers_bucket` (default: "qualifiers")
- `s3_snaks_bucket` (default: "snaks")
- `s3_terms_bucket` (default: "terms")
- `s3_sitelinks_bucket` (default: "sitelinks")
- `s3_lexeme_forms_bucket` (default: "lexeme-forms")
- `s3_lexeme_senses_bucket` (default: "lexeme-senses")

#### Create Tables

Creates all required Vitess tables:

```bash
python -m models.workers.dev create_tables
```

**Tables Created**:
- `id_ranges`
- `entity_head`
- `entity_revisions`
- `entity_redirects`
- `entity_backlinks`
- `statement_content`
- `users`
- `user_thanks`
- `user_statement_endorsements`
- `user_watchlist`
- `watchlist_notifications`
- `user_daily_stats`
- `general_daily_stats`
- `backlink_statistics`
- `metadata`
- `lexeme_terms`

### Usage

```bash
# Initialize S3 buckets
python -m models.workers.dev create_buckets

# Initialize database tables
python -m models.workers.dev create_tables

# Full initialization
python -m models.workers.dev create_buckets && python -m models.workers.dev create_tables
```

### Health Checks

Not applicable (on-demand tool only).

---

## Worker Configuration Reference

### Common Settings

All workers support these settings:

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `log_level` | str | "INFO" | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `environment` | str | "prod" | Environment (prod, dev, test) |

### Database Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `vitess_host` | str | - | Vitess database host |
| `vitess_port` | int | - | Vitess database port |
| `vitess_database` | str | - | Vitess database name |
| `vitess_user` | str | - | Vitess database user |
| `vitess_password` | str | - | Vitess database password |

### S3 Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `s3_endpoint` | str | "http://minio:9000" | S3 endpoint |
| `s3_access_key` | str | - | S3 access key |
| `s3_secret_key` | str | - | S3 secret key |
| `s3_*_bucket` | str | - | S3 bucket names |

### Kafka Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `kafka_brokers` | str | - | Kafka broker addresses |
| `kafka_entitychange_json_topic` | str | "entitybase.entity_change" | Entity change topic |
| `kafka_entity_diff_topic` | str | "wikibase.entity_diff" | Entity diff topic |

---

## Worker Deployment

### Docker Compose

Workers are configured in `docker-compose.yml`:

```yaml
services:
  id-generation-worker:
    image: wikibase-backend
    command: python -m models.workers.id_generation.id_generation_worker
    environment:
      - VITESS_HOST=vitess
      - S3_ENDPOINT=http://minio:9000

  entity-diff-worker:
    image: wikibase-backend
    command: python -m models.workers.entity_diff.entity_diff_worker
    depends_on:
      - kafka
```

### Manual Execution

```bash
# Run worker directly
python -m models.workers.id_generation.id_generation_worker

# Run with custom settings
export VITESS_HOST=localhost
export LOG_LEVEL=DEBUG
python -m models.workers.entity_diff.entity_diff_worker
```

---

## Monitoring and Observability

### Health Endpoints

All workers expose a health endpoint:

```bash
GET /workers/{worker_name}/health

Response:
{
  "status": "running",
  "last_heartbeat": "2025-01-15T10:30:00Z",
  "uptime_seconds": 3600
}
```

### Logging

Workers use structured logging:

```python
logger.info("Processing entity", entity_id="Q123", revision_id=42)
logger.error("Failed to process", entity_id="Q123", error=str(e))
```

### Metrics

Recommended Prometheus metrics:

- `worker_up`: Worker running status
- `worker_jobs_total`: Number of jobs processed
- `worker_jobs_failed_total`: Number of failed jobs
- `worker_job_duration_seconds`: Job processing time
- `worker_queue_length`: Queue length (if applicable)

---

## Related Documentation

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Overall system architecture
- [STORAGE-ARCHITECTURE.md](./STORAGE-ARCHITECTURE.md) - S3 and Vitess storage
- [CONFIGURATION.md](./CONFIGURATION.md) - Configuration options
- [ARCHITECTURE-CHANGELOG.md](./ARCHITECTURE-CHANGELOG.md) - Worker changes history
