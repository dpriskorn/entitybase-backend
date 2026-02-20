# Incremental RDF Updater

## Overview

The Incremental RDF Updater is a worker service that consumes entity change events and generates incremental RDF diffs for downstream consumers. It provides real-time RDF updates by computing differences between entity versions, enabling applications to maintain up-to-date RDF representations without regenerating full dumps.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Incremental RDF Updater                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────┐    ┌───────────────────┐                     │
│  │  Kafka Consumer  │───▶│ IncrementalRDF    │                     │
│  │ (entity_change)  │    │ Worker            │                     │
│  └──────────────────┘    └─────────┬─────────┘                     │
│                                     │                               │
│                                     ▼                               │
│  ┌──────────────────┐    ┌───────────────────┐                     │
│  │  Kafka Producer  │◀───│ IncrementalRDF    │                     │
│  │ (incremental_    │    │ Updater            │                     │
│  │  rdf_diff)       │    └───────────────────┘                     │
│  └──────────────────┘                       │                       │
│                                     ┌───────┴───────┐               │
│                                     ▼               ▼               │
│                              ┌─────────────┐  ┌─────────────┐       │
│                              │  Vitess     │  │     S3      │       │
│                              │  (metadata) │  │  (snapshots) │       │
│                              └─────────────┘  └─────────────┘       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Components

### IncrementalRDFWorker

**Location**: `models/workers/incremental_rdf/incremental_rdf_worker.py`

Main worker that orchestrates the pipeline:

1. Consumes entity change events from `entitybase.entity_change` Kafka topic
2. Looks up revision metadata in Vitess (MySQL) to get content hashes
3. Fetches entity snapshots from S3 for both old and new revisions
4. Computes RDF diffs using `IncrementalRDFUpdater`
5. Publishes RDF change events to `incremental_rdf_diff` Kafka topic

### IncrementalRDFUpdater

**Location**: `models/rdf_builder/incremental_updater.py`

Handles diff computation between two entity versions:

- Computes statement diffs (added/removed statements)
- Computes terms diffs (labels, descriptions, aliases)
- Computes sitelinks diffs
- Applies diffs to generate incremental RDF output

### RDFChangeEventBuilder

**Location**: `models/workers/incremental_rdf/rdf_change_builder.py`

Builds RDF change events following the `entity_diff/2.0.0` schema:

- `RDFChangeEvent` - Main event model
- `RDFDataField` - RDF data with mime type
- Supports operations: `import`, `diff`, `delete`, `reconcile`

## Data Flow

```
┌─────────────────┐
│ Entity Change   │
│ Event           │
│ (Kafka)         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Parse event:    │
│ - entity_id     │
│ - revision_id   │
│ - from_revision │
│ - change_type   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│ Fetch old       │     │ Fetch new      │
│ revision from   │     │ revision from  │
│ S3 (optional)   │     │ S3              │
└────────┬────────┘     └────────┬────────┘
         │                        │
         └────────┬───────────────┘
                  ▼
┌─────────────────┐
│ Compute diffs:  │
│ - statements   │
│ - terms        │
│ - sitelinks    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Build RDF      │
│ Change Event   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Publish to     │
│ incremental_   │
│ rdf_diff topic │
└─────────────────┘
```

## Kafka Topics

| Topic | Direction | Description |
|-------|-----------|-------------|
| `entitybase.entity_change` | Input | Entity change events from the entitybase system |
| `incremental_rdf_diff` | Output | RDF change events with diffs for downstream consumers |

Topic names are configurable via environment variables.

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `INCREMENTAL_RDF_ENABLED` | `false` | Enable or disable the worker |
| `INCREMENTAL_RDF_CONSUMER_GROUP` | `incremental-rdf-worker` | Kafka consumer group ID |
| `KAFKA_INCREMENTAL_RDF_TOPIC` | `incremental_rdf_diff` | Output Kafka topic for RDF changes |
| `KAFKA_ENTITY_CHANGE_TOPIC` | `entitybase.entity_change` | Input Kafka topic for entity changes |
| `KAFKA_BOOTSTRAP_SERVERS` | - | Comma-separated list of Kafka broker addresses |
| `S3_ENDPOINT` | - | S3 endpoint URL (e.g., http://localhost:9000) |
| `S3_ACCESS_KEY` | - | S3 access key |
| `S3_SECRET_KEY` | - | S3 secret key |
| `S3_BUCKET` | - | S3 bucket name for entity snapshots |

## Output Schema

The output follows the `entity_diff/2.0.0` schema:

```json
{
  "$schema": "/mediawiki/wikibase/entity/rdf_change/2.0.0",
  "dt": "2024-01-01T00:00:00Z",
  "entity_id": "Q42",
  "meta": {
    "domain": "wikibase.org",
    "stream": "incremental_rdf_diff",
    "request_id": "uuid"
  },
  "operation": "diff",
  "rev_id": 12345,
  "rdf_added_data": {
    "data": "<triples> .",
    "mime_type": "text/turtle"
  },
  "rdf_deleted_data": {
    "data": "<triples> .",
    "mime_type": "text/turtle"
  },
  "sequence": 0,
  "sequence_length": 1
}
```

### Operations

| Operation | Description | RDF Data |
|-----------|-------------|----------|
| `import` | New entity created or restored | Full RDF in `rdf_added_data` |
| `diff` | Entity edited (new revision) | Added triples in `rdf_added_data`, removed in `rdf_deleted_data` |
| `delete` | Entity deleted | No RDF data |
| `reconcile` | Prior data may no longer be trusted | No RDF data |

## Troubleshooting

### Missing S3 Data

**Symptom**: Worker logs error "Failed to fetch entity data for Q42 rev 12345"

**Cause**: The requested revision is not available in S3 storage

**Solution**:
- Verify S3 bucket contains the expected revision
- Check S3 versioning configuration matches expected version
- Ensure entity snapshots are being written to S3 on entity changes

### Missing from_revision_id

**Symptom**: First edit to an entity always triggers an `import` operation

**Cause**: Entity change events for first edits don't include `from_revision_id`

**Solution**: This is expected behavior - the worker treats missing `from_revision_id` as a new entity import

### Diff Computation Failures

**Symptom**: Worker logs warning "Failed to compute diffs"

**Cause**: Unable to convert entity data to internal representation

**Solution**:
- Check entity data format in S3 matches expected JSON structure
- Review entity parsing errors in logs
- The worker will publish a partial event even if diff computation fails

### Kafka Connection Issues

**Symptom**: Worker fails to start with "Kafka not configured"

**Cause**: `KAFKA_BOOTSTRAP_SERVERS` not set or unreachable

**Solution**:
- Verify `KAFKA_BOOTSTRAP_SERVERS` environment variable is set
- Check Kafka broker connectivity
- Review worker logs for specific connection errors

### Consumer Lag

**Symptom**: Events processed with significant delay

**Cause**: High volume of entity changes or worker processing is slow

**Solution**:
- Scale worker horizontally (multiple consumer instances with same group ID)
- Check worker resource usage (CPU, memory)
- Review S3 fetch latency

## Limitations

1. **Simplified RDF Diff**: The current `IncrementalRDFUpdater` implementation produces simplified output (comment annotations) rather than actual RDF triples. This is a placeholder implementation.

2. **S3 Dependency**: The worker requires entity snapshots to be stored in S3. If S3 is not configured or unavailable, the worker cannot process changes.

3. **No Vitess Content Hash Lookup**: Currently, the worker fetches entity data directly from S3 without using Vitess content hashes for verification. Future versions may add this for improved consistency checking.

4. **Single-Part Events**: The current implementation always produces single-part events (`sequence_length: 1`). Large entity changes that require chunking are not yet supported.

5. **No Retry Mechanism**: Failed message processing does not include automatic retry. Consider implementing dead letter queue (DLQ) handling for production deployments.
