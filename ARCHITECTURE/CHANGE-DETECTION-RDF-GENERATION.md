# Change Detection and RDF Generation Architecture

## Overview

This document describes the services for generating RDF from entity snapshots and producing both continuous RDF change streams and weekly entity dumps (JSON + RDF formats). The change detection component is documented separately in [MEDIAWIKI-INDEPENDENT-CHANGE-DETECTION.md](./MEDIAWIKI-INDEPENDENT-CHANGE-DETECTION.md).

## Requirements

1. **Weekly Dumps**: Generate complete dumps of all recent entities in both JSON and RDF formats weekly
2. **Continuous Streaming**: Stream recent changes as RDF patches in real-time
3. **Architecture Alignment**: Integrate with existing S3 + Vitess storage model

---

## Current Architecture Dependencies

### Storage Infrastructure

| Component | Data Stored | Purpose |
|-----------|-------------|---------|
| **S3** | Immutable revision snapshots (full entity JSON) | System of record for all entity content |
| **Vitess** | Metadata only (`entity_head`, `entity_revisions`) | Pointers to S3, revision history, deletion audit |

### Existing Data Flow

```
Client API → Validate → Assign revision_id → S3 snapshot → Vitess metadata → MediaWiki event
```

### Limitation

- **MediaWiki Dependency**: Change events only emitted by MediaWiki EventBus
- **No Change History in Storage**: Vitess stores revision metadata, but no computed changes
- **Backfill Impossible**: Cannot compute historical changes without MediaWiki events

---

## Service 1: JSON→RDF Converter

**Purpose**: Convert Wikibase JSON snapshots to RDF (Turtle format) using streaming generation

**Conversion Mapping** (based on Wikibase RDF mapping rules):

| JSON Field | RDF Triple Pattern |
|-----------|------------------|
| Entity ID | `<entity_uri> a wikibase:Item .` |
| Labels | `<entity_uri> rdfs:label "label"@lang .` |
| Descriptions | `<entity_uri> schema:description "description"@lang .` |
| Aliases | `<entity_uri> skos:altLabel "alias"@lang .` |
| Claims | `<entity_uri> p:P<property> [statement] .` |
| Sitelinks | `<entity_uri> schema:sameAs <wiki_url> .` |

**Implementation - Streaming Approach** (critical for 1M+ entities/week scale):

```python
def json_stream_to_rdf_turtle(json_input: io.TextIO, ttl_output: io.TextIO):
    """Stream JSON to RDF without loading full entity in memory"""
    
    # Write Turtle header once
    ttl_output.write("""@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix wd: <http://www.wikidata.org/entity/> .
@prefix p: <http://www.wikidata.org/prop/direct/> .

""")
    
    # Stream entities line-by-line
    for line in json_input:
        entity = json.loads(line)
        entity_uri = f"http://www.wikidata.org/entity/{entity['id']}"
        
        # Write entity triples immediately (don't build full string)
        ttl_output.write(f"\n# Entity: {entity_uri}\n")
        ttl_output.write(f"<{entity_uri}> a wikibase:Item .\n")
        
        # Stream labels
        for lang, label in entity.get('labels', {}).items():
            ttl_output.write(f'<{entity_uri}> rdfs:label "{escape_turtle(label)}"@{lang} .\n')
        
        # Stream claims (claim-by-claim, not all at once)
        for prop_id, claims in entity.get('claims', {}).items():
            for claim in claims:
                statement_uri = generate_statement_uri(claim['id'])
                ttl_output.write(f'<{entity_uri}> p:{prop_id} {statement_uri} .\n')
                ttl_output.write(f'{statement_uri} a wikibase:Statement .\n')
                
                # Write claim values immediately
                write_statement_values(ttl_output, statement_uri, claim)
        
        ttl_output.write(f"\n# --- End entity: {entity_uri} ---\n\n")
        
        # Flush periodically (every 1000 triples)
        if ttl_output.triple_count % 1000 == 0:
            ttl_output.flush()
```

**Optimizations** (for scale):
1. **Caching**: Cache frequent RDF prefixes and templates
   ```python
   TURTLE_PREFIXES = """@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix wd: <http://www.wikidata.org/entity/> .
@prefix p: <http://www.wikidata.org/prop/direct/> .
"""
   
   CLAIM_TEMPLATE = """{entity_uri} p:{prop_id} {statement_uri} .
{statement_uri} a wikibase:Statement .
"""   ```

2. **Parallel Claim Conversion** (one thread per property group):
   ```python
   from concurrent.futures import ThreadPoolExecutor
   
   def process_property_group(entity, property_ids):
       for prop_id in property_ids:
           claims = entity['claims'].get(prop_id, [])
           for claim in claims:
               write_claim_triples(ttl_output, claim)
   
   # Group properties by claim count (light vs heavy entities)
   executor = ThreadPoolExecutor(max_workers=10)
   executor.map(lambda props: process_property_group(entity, props), property_groups)
   ```

3. **Streaming Turtle Generation**: Write line-by-line, never build full document in memory
   - Avoid OOM on entities with 1000+ claims
   - Flush output buffer periodically (every 1000 triples)

**Technology Stack**:
- RDF libraries: rdflib (Python), RDF4J (Java), Apache Jena (Java)
- Template engine: Jinja2, Mustache for Turtle templates
- Streaming: Process large entities without full in-memory load

---

## Service 2: Weekly Dump Generator

**Purpose**: Generate weekly dumps of all entities in both JSON and RDF formats as standalone S3 files

**Critical Design Decision**: Weekly dumps are FILES, not Kafka events. The `rdf_change` schema is NOT used for weekly dumps - use standard Turtle format directly.

**Data Flow**:
```
Weekly Scheduler (Cron/Airflow)
          ↓
    Query entity_head: Get all entities
          ↓
    Batch fetch S3 snapshots (parallel, 1000s at a time)
          ↓
    ┌──────────────────────────────────┐
    ↓                              ↓
Convert to JSON Dump           Convert to RDF (Turtle) - Streaming
    ↓                              ↓
Write to S3:                     Write to S3:
  dump/YYYY-MM-DD/full.json       dump/YYYY-MM-DD/full.ttl
  (optional partitioned)          (optional partitioned)
```
Weekly Scheduler (Cron/Airflow)
          ↓
    Query entity_head: Get all entities
          ↓
    Batch fetch S3 snapshots (parallel, 1000s at a time)
          ↓
    ┌──────────────────────────────────┐
    ↓                              ↓
Convert to JSON Dump           Convert to RDF (Turtle) - Streaming
    ↓                              ↓
Write to S3:                     Write to S3:
  dump/YYYY-MM-DD/full.json       dump/YYYY-MM-DD/full.ttl
  (optional partitioned)          (optional partitioned)
```

**Critical Design Decision**: Weekly dumps are FILES, not Kafka events. The `rdf_change` schema is NOT used for weekly dumps - use standard Turtle format directly.

**Implementation Design**:

#### Step 1: Query Changed Entities
```sql
SELECT DISTINCT h.entity_id, h.head_revision_id, h.updated_at
FROM entity_head h
WHERE h.updated_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
ORDER BY h.updated_at ASC;
```

#### Step 2: Batch Fetch S3 Snapshots
```python
def fetch_snapshots_in_batches(entity_ids: List[str], batch_size: int = 1000):
    """Fetch S3 snapshots in parallel batches"""
    for batch_start in range(0, len(entity_ids), batch_size):
        batch = entity_ids[batch_start:batch_start + batch_size]

        # Build S3 URIs
        uris = [
            f"s3://bucket/{entity_id}/r{revision_id}.json"
            for entity_id, revision_id in batch
        ]

        # Fetch in parallel
        snapshots = s3_client.get_objects(uris)

        # Process batch
        yield snapshots
```

#### Step 3: Generate Outputs

**JSON Dump Format**:
```json
{
  "dump_metadata": {
    "generated_at": "2025-01-15T00:00:00Z",
    "time_range": "2025-01-08T00:00:00Z/2025-01-15T00:00:00Z",
    "entity_count": 1234567,
    "format": "canonical-json"
  },
  "entities": [
    {
      "entity": { ...full entity JSON... },
      "metadata": {
        "revision_id": 327,
        "entity_id": "Q42",
        "s3_uri": "s3://bucket/Q42/r327.json"
      }
    },
    ...
  ]
}
```

**RDF Dump Format** (Turtle):
```turtle
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix wd: <http://www.wikidata.org/entity/> .
@prefix p: <http://www.wikidata.org/prop/direct/> .

# Dump metadata
[] a schema:DataDownload ;
    schema:dateModified "2025-01-15T00:00:00Z"^^xsd:dateTime ;
    schema:temporalCoverage "2025-01-08T00:00:00Z/2025-01-15T00:00:00Z" ;
    schema:numberOfItems 1234567 ;
    dcat:downloadURL <https://s3.amazonaws.com/bucket/dump/2025-01-15/full.ttl> .

# Entity Q42
wd:Q42 a wikibase:Item ;
    rdfs:label "Douglas Adams"@en ;
    rdfs:label "Douglas Adams"@de ;
    schema:description "English writer and humorist"@en ;
    ...

# Entity Q123
wd:Q123 a wikibase:Item ;
    ...
```

**S3 Output Structure**:
```
s3://wikibase-dumps/
  weekly/
    2025/
      01/
        15/
          full.json              # Complete JSON dump
          full.ttl               # Complete RDF (Turtle) dump
          part-00001.ttl         # Optional split for large datasets
          part-00002.ttl
          ...
          metadata.json          # Dump metadata with generation info
          manifest.txt            # Optional checksums for validation
```

**Configuration**:
| Option | Description | Default |
|---------|-------------|---------|
| `schedule` | Cron expression for weekly dumps | `0 2 * * 0` (Sunday 2AM) |
| `s3_dump_bucket` | S3 bucket for dumps | wikibase-dumps |
| `batch_size` | Entities per batch | 1000 |
| `parallel_workers` | Parallel conversion threads | 10 |
| `format_versions` | JSON and RDF formats to generate | `["canonical-1.0", "turtle-1.1"]` |
| `compression` | Output compression | `gzip` |

---

## Service 3: Continuous RDF Change Streamer

See [CONTINUOUS-RDF-CHANGE-STREAMER.md](./CONTINUOUS-RDF-CHANGE-STREAMER.md) for complete documentation.

**Purpose**: Convert entity changes to RDF patches and stream continuously

**Architecture**:
```
Change Detection Service (see MEDIAWIKI-INDEPENDENT-CHANGE-DETECTION.md)
            ↓ (entity change events)
       JSON→RDF Converter
            ↓
      Compute RDF Diff (between two RDF representations)
            ↓
       Emit rdf_change events (Kafka)
            ↓
   WDQS Consumer / Other Consumers
            ↓
        Apply patches to Blazegraph
```

**Key Features**:
- Real-time RDF diff computation using Option A (Full RDF Convert + Diff)
- Import mode for large entities (>10K triples)
- Event-driven architecture with Kafka
- Scalable parallel processing
- Comprehensive error handling and monitoring

---

## Complete Integrated Architecture

### Full Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Client API                                   │
│                           ↓                                       │
│                      Validate Entity                                 │
│                           ↓                                       │
│                   Assign Revision ID                                  │
│                           ↓                                       │
│                    Write S3 Snapshot                                │
│                           ↓                                       │
│                    Insert Vitess Metadata                             │
│                           ↓                                       │
│                  Emit MediaWiki Change Event (existing)              │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     │ Change Detection Service
                                     │ (see MEDIAWIKI-INDEPENDENT-CHANGE-DETECTION.md)
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  RDF Generation Services                                         │
│                                                                  │
│                    Entity Changes (from Change Detection)               │
│                            ↓                                     │
│              ┌──────────────┴─────────────────────────┐                 │
│              ↓                                      │                  │
│    Continuous RDF Change Stream          Weekly RDF Dump Service    │
│         (Real-time)                        (Scheduled)                │
│              ↓                                      ↓                  │
│    JSON→RDF Converter              JSON→Turtle Dump Converter       │
│              ↓                                      ↓                  │
│    Compute RDF Diff                      Batch RDF Generation          │
│              ↓                                      ↓                  │
│    Emit rdf_change events              Write S3: full.ttl           │
│    (Kafka)                              (with metadata)               │
└─────────────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Kafka Topic                                │
│                                                                  │
│  Topic: wikibase.rdf_change (reuse or new)                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Consumers                                      │
│                                                                  │
│  ┌──────────────────────┐  ┌──────────────────────┐                │
│  │   WDQS Consumer   │  │  Search Indexer    │                │
│  │ (reuse existing)  │  │   (optional)        │                │
│  │                   │  │                    │                │
│  │ - Apply patches    │  │ - Index from dump   │                │
│  │   to Blazegraph   │  │ - Stream updates    │                │
│  │                   │  │                    │                │
│  └──────────────────────┘  └──────────────────────┘                │
│                                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Summary

| Component | Inputs | Outputs | Technology |
|-----------|---------|----------|------------|
| **Change Detection** | entity_head + entity_revisions + S3 snapshots | Entity change events | See MEDIAWIKI-INDEPENDENT-CHANGE-DETECTION.md |
| **JSON→RDF Converter** | Entity JSON snapshots | RDF (Turtle format) | Python/Scala/Java |
| **Weekly RDF Dump Service** | entity_head + S3 snapshots (all recent entities) | S3: weekly JSON + RDF dump files | Python/Scala |
| **Continuous RDF Change Streamer** | Entity change events | `rdf_change` events (Kafka) | Python/Scala/Go |
| **Existing WDQS Consumer** | `rdf_change` events (Kafka) | Apply patches to Blazegraph | Java (existing) |

---

## Implementation Phases

### Phase 1: Change Detection (2-3 weeks)
- See [MEDIAWIKI-INDEPENDENT-CHANGE-DETECTION.md](./MEDIAWIKI-INDEPENDENT-CHANGE-DETECTION.md) for implementation details
- Build Change Detector service
- Implement entity_head polling logic
- Add metrics and monitoring
- Deploy to staging

### Phase 2: RDF Conversion (2-3 weeks)
- [ ] Implement JSON→Turtle converter
- [ ] Test conversion fidelity with Wikidata examples
- [ ] Build RDF diff computation (using Jena/RDF4J) - see [RDF-DIFF-STRATEGY.md](./RDF-DIFF-STRATEGY.md)
- [ ] Validate RDF output against Blazegraph

### Phase 3: Weekly Dumps (2-3 weeks)
- [ ] Implement batch fetch logic
- [ ] Build JSON dump formatter
- [ ] Build RDF dump formatter
- [ ] Add compression and S3 upload
- [ ] Set up weekly cron schedule
- [ ] Implement manifest and checksum generation

### Phase 4: Continuous RDF Streaming (2 weeks)
- See [CONTINUOUS-RDF-CHANGE-STREAMER.md](./CONTINUOUS-RDF-CHANGE-STREAMER.md) for implementation details
- [ ] Integrate Change Detection with RDF Converter
- [ ] Implement event consumption and emission
- [ ] Set up monitoring and metrics
- [ ] Deploy to staging

### Phase 5: Integration & Testing (2 weeks)
- [ ] Integrate all components
- [ ] End-to-end testing with sample entities
- [ ] Performance testing (latency, throughput)
- [ ] Deploy to production
- [ ] Set up monitoring and alerting

---

## Advantages

| Benefit | Description |
|----------|-------------|
| **MediaWiki Independence** | See [MEDIAWIKI-INDEPENDENT-CHANGE-DETECTION.md](./MEDIAWIKI-INDEPENDENT-CHANGE-DETECTION.md) |
| **Backfill Capable** | Can process historical changes from any point in time |
| **Deterministic** | Based on immutable snapshots and ordered revision metadata |
| **Scalable** | All services can scale independently (S3, Vitess, Kafka) |
| **Dual Output** | Supports both continuous streaming (diffs) and batch dumps (full snapshots) |
| **Flexible** | Multiple consumers can use outputs (WDQS, search, analytics, mirrors) |

---

## Open Questions

1. **Change Granularity**: Entity-level diffs or claim-level diffs for RDF stream?
2. **Backfill Strategy**: Should we process historical changes (from existing revisions) on initial deployment? No
3. **Snapshot Retention**: How long to keep weekly dumps in S3? Lifecycle rules? 1y rolling
4. **Performance Targets**: Latency targets for change detection? What's acceptable polling interval?
5. **Weekly Dump Partitioning**: Single file vs. multiple partitions at 1M entities/week scale? Multiple
6. **Consumer Coordination**: Should we use existing MediaWiki events or S3-based change detection (or both)? existing if possible at first
7. **RDF Change Strategy**: See [RDF-DIFF-STRATEGY.md](./RDF-DIFF-STRATEGY.md) for details on Option A (Full RDF Convert + Diff)

---

## Architecture Notes

### Consume MediaWiki Events

If MediaWiki EventBus continues emitting change events, the simplest approach is:

```
MediaWiki Events → Fetch Entity from S3 → Convert to RDF → Emit rdf_change
```

This requires no change detection at all - just convert MediaWiki events to RDF format.

## References

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Core architecture principles
- [STORAGE-ARCHITECTURE.md](./STORAGE-ARCHITECTURE.md) - S3 + Vitess storage model
- [MEDIAWIKI-INDEPENDENT-CHANGE-DETECTION.md](./MEDIAWIKI-INDEPENDENT-CHANGE-DETECTION.md) - Change detection service documentation
- [CONTINUOUS-RDF-CHANGE-STREAMER.md](./CONTINUOUS-RDF-CHANGE-STREAMER.md) - Continuous RDF change streamer service
- [RDF-DIFF-STRATEGY.md](./RDF-DIFF-STRATEGY.md) - RDF diff strategy (Option A: Full Convert + Diff)
- [CHANGE-NOTIFICATION.md](./CHANGE-NOTIFICATION.md) - Existing event notification system
- [SCHEMAS-EVENT-PRIMARY-SUMMARY.md](../SCHEMAS-EVENT-PRIMARY-SUMMARY.md) - RDF change schema documentation
- [STREAMING-UPDATER-PRODUCER.md](../STREAMING-UPDATER-PRODUCER.md) - Existing MediaWiki→RDF pipeline
- [STREAMING-UPDATER-CONSUMER.md](../STREAMING-UPDATER-CONSUMER.md) - Existing RDF consumer for Blazegraph
