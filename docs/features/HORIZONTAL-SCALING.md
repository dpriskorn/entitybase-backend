# Horizontal Scaling

Built for billion-scale operations with horizontal scaling.

## Overview

Entitybase is designed from the ground up to scale to 1 billion+ entities and 1 trillion+ statements. The architecture separates storage (S3) from indexing (Vitess), enabling independent scaling.

## Scaling Strategy

### Storage Layer (S3)
- **Immutable snapshots** — Append-only writes avoid update hotspots
- **Infinite capacity** — Object storage scales automatically
- **Cost-effective** — Pay only for what you store

### Indexing Layer (Vitess)
- **Sharding** — Scale horizontally by entity ID ranges
- **Read replicas** — Distribute read load
- **Range-based ID allocation** — Prevents write hotspots

### Workers
- **ID Generator** — Range-based allocation for Q/P/L IDs
- **Dump Worker** — Parallelized entity exports
- **RDF Streamer** — Continuous RDF generation

## Performance Targets

| Metric | Target |
|--------|--------|
| Entity Creation | 777K/day sustained |
| Read Latency | Sub-millisecond |
| Storage | 2.84B entities over 10 years |

## Scaling Characteristics

- **Write throughput** — 10 edits/sec with 90% new entities
- **Horizontal sharding** — By entity ID ranges
- **No single point of failure** — Stateless API workers

See also: [Architecture](../ARCHITECTURE/ARCHITECTURE.md), [Scaling Properties](../ARCHITECTURE/SCALING-PROPERTIES.md)
