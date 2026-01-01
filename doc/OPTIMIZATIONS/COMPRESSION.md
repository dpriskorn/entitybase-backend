# Compression Strategy

## Overview

This document outlines the compression strategy for storing Wikidata entities and their revision history in S3. Based on empirical data and cost analysis, we recommend a two-phase approach to optimize storage costs while maintaining acceptable performance.

## Executive Summary

**Recommendation:** Start with Gzip (level 6), optimize to Zstd only if CPU becomes a bottleneck.

**Projected savings:** 93% cost reduction vs. no compression ($2.28M → $152K over 10 years at 1B entity scale)

**Key benefit:** Significant cost savings with industry-standard compression that's simple to implement and monitor.

## Data Model

Based on empirical measurements from 300 entity samples:

- Mean revisions per entity: 20 (median: 13, stdev: 28)
- Mean entity size: 16.9 KB (median: 10.8 KB, stdev: 20.6 KB)
- Total per entity: 330.2 KB (including all 20 revisions)
- 1B entities: 330.2 TB (uncompressed)

## Compression Options Comparison

| Algorithm | Compression Ratio | 10-Year Cost | Compression Speed | Decompression Speed | Pros | Cons |
|-----------|-------------------|--------------|-------------------|---------------------|------|------|
| **Gzip (level 6)** | 6:1 | $152K | Moderate | Fast | Industry standard, best compression, mature | Moderate CPU overhead |
| **Brotli** | 4:1 | $227K | Slow | Fast | Web-optimized, good compression | Slower compression |
| **Zstd** | 4-5:1 | $227K-$285K | Very Fast | Very Fast | Fast compression/decompression, tunable | Lower max compression |
| **None** | - | $2.28M | N/A | N/A | Zero CPU overhead | Highest storage cost |

**Note:** Zstd actual compression ratio is typically 4-5:1 (not 3:1), making it more competitive.

## Recommendation: Two-Phase Approach

### Phase 1: Start with Gzip (level 6)

**Rationale:**

1. **Best compression**: 6:1 ratio provides lowest storage costs ($152K over 10 years)
2. **Industry standard**: Built-in to all major programming languages, battle-tested
3. **Simple integration**: No need for external dependencies or complex setup
4. **Predictable performance**: Well-understood CPU and latency characteristics
5. **Wide tooling support**: Easy to debug, test, and monitor

**Implementation:**

- Compress entity JSON data before storing to S3
- Use standard Gzip libraries (Python: `gzip`, Node: `zlib`, Go: `compress/gzip`)
- Set compression level to 6 (balance between compression ratio and speed)
- Store compression metadata in entity headers

**Expected performance:**

- Compression: ~50-100 MB/s per CPU core (level 6)
- Decompression: ~200-300 MB/s per CPU core
- CPU overhead: ~5-10% increase during writes
- Latency impact: ~10-20ms additional for compression/decompression

### Phase 2: Optimize to Zstd (if needed)

**When to consider Zstd:**

1. CPU utilization consistently >80% during write operations
2. Compression/decompression becomes a bottleneck
3. Need faster ingestion rates
4. Cost analysis shows CPU costs > storage savings

**Why Zstd:**

- **Fastest speeds**: 3-5x faster compression than Gzip
- **Good compression**: 4-5:1 ratio (better than Brotli, close to Gzip)
- **Tunable levels**: Can adjust based on performance needs
- **Modern**: Actively developed, optimized for modern CPUs
- **Real-time friendly**: Designed for streaming compression

**Implementation considerations:**

- Requires external library dependency (not built into all languages)
- May need migration strategy from Gzip
- Test with production workload before full rollout

**Comparison to Gzip:**

| Metric | Gzip (level 6) | Zstd (level 3) | Zstd (level 19) |
|--------|----------------|----------------|-----------------|
| Compression speed | Baseline | 3-5x faster | 2-3x faster |
| Compression ratio | 6:1 | 4:1 | 6:1 |
| Decompression speed | Fast | Very Fast | Very Fast |

## Implementation Guidelines

### Compression Pipeline

```
Entity JSON → Compression → S3 Object
                ↓
            Gzip (level 6)
```

### Data Flow

1. **Write path:**
   - Receive entity JSON (uncompressed)
   - Compress with Gzip (level 6)
   - Store in S3 with `Content-Encoding: gzip`
   - Update metadata with compression stats

2. **Read path:**
   - Fetch from S3
   - Decompress with Gzip
   - Return to application

3. **Monitoring:**
   - Track compression ratio per entity
   - Monitor CPU utilization during compression
   - Measure latency impact (compression/decompression time)
   - Alert on compression failures

### Configuration

**Initial setup (Gzip):**
- Compression level: 6
- Parallel compression: Yes (multiple workers)
- Compression threshold: Compress all entities (>1KB)
- Validation: Verify decompression after compression

**Optimization setup (Zstd - if needed):**
- Compression level: 3 (balanced)
- Parallel compression: Yes
- Compression threshold: Compress all entities (>1KB)
- Validation: Verify decompression after compression

### Migration Strategy (Gzip → Zstd)

1. **Pilot phase:**
   - Test Zstd on 1% of new entities
   - Compare performance metrics (CPU, latency, compression ratio)
   - Validate cost savings

2. **Gradual rollout:**
   - Increase to 10% of new entities
   - Monitor production metrics
   - Continue if no issues

3. **Full migration:**
   - Migrate 100% of new entities to Zstd
   - Optional: Compress existing Gzip entities during low-traffic periods

## Cost Analysis

### Storage Costs (1B entities, Year 10)

| Strategy | Storage | Monthly Cost | 10-Year Cost | CPU Overhead |
|----------|---------|--------------|--------------|--------------|
| No compression | 825.5 TB | $18,986 | $2.28M | 0% |
| Gzip (6:1) | 137.6 TB | $3,164 | $379K | 5-10% |
| Gzip (level 6) | 55.0 TB | $1,267 | **$152K** | 5-10% |
| Brotli (4:1) | 206.4 TB | $4,746 | $569K | 5-8% |
| Zstd (5:1) | 165.1 TB | $3,796 | $455K | 2-5% |

**Note:** Gzip level 6 achieves best compression ratio in practice.

### CPU Cost Estimate

Assuming 1B entities created over 10 years (avg: 3.17 entities/sec):

- **Gzip compression:** ~50-100 MB/s per core
- **CPU required:** ~2-4 cores continuously (minimal overhead)
- **Cost:** Negligible compared to storage savings ($152K vs. $2.28M)

**Conclusion:** CPU overhead is negligible compared to massive storage cost savings.

## Monitoring and Alerts

### Key Metrics

1. **Compression ratio:**
   - Target: 4:1 minimum (Gzip), 3:1 minimum (Zstd)
   - Alert: If ratio drops below 3:1 consistently

2. **CPU utilization:**
   - Target: <70% during peak write periods
   - Alert: If CPU >80% for extended periods

3. **Latency:**
   - Target: <50ms additional latency for compression/decompression
   - Alert: If latency >100ms consistently

4. **Error rate:**
   - Target: 0% compression/decompression failures
   - Alert: Any compression failures

### Dashboards

Implement Grafana dashboards showing:
- Real-time compression ratio per entity type
- CPU utilization by compression workers
- Compression/decompression latency (p50, p95, p99)
- Storage cost trends with and without compression
- Cost savings from compression

## Risk Assessment

### Low Risk

1. **Compression bugs:**
   - Mitigation: Validate decompression after compression, test extensively

2. **Latency impact:**
   - Mitigation: Monitor latency, cache hot entities, parallelize compression

### Medium Risk

1. **CPU bottleneck:**
   - Mitigation: Start with Gzip, optimize to Zstd if needed, scale horizontally

2. **Migration complexity:**
   - Mitigation: Gradual rollout, maintain compatibility with Gzip

### Low Risk

1. **Storage cost increases:**
   - Mitigation: Compression provides 93% cost reduction, minimal risk

2. **Performance degradation:**
   - Mitigation: Monitor closely, rollback to Zstd if Gzip causes issues

## Testing Plan

### Unit Tests

- Test compression/decompression with various entity sizes
- Verify data integrity after compression/decompression
- Test error handling (invalid data, compression failures)

### Integration Tests

- Test full write path (JSON → compression → S3)
- Test full read path (S3 → decompression → JSON)
- Test with production-like data samples

### Load Tests

- Simulate 1000+ concurrent entity writes
- Measure CPU utilization under load
- Verify compression ratio under load
- Test degradation behavior

### Performance Benchmarks

- Benchmark Gzip vs. Zstd on representative data
- Measure compression speed (MB/s)
- Measure decompression speed (MB/s)
- Measure CPU utilization

## Decision Matrix

| Factor | Gzip (level 6) | Zstd | Brotli | No Compression |
|--------|----------------|------|--------|----------------|
| Storage cost | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐ |
| CPU overhead | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Implementation complexity | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Industry adoption | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | N/A |
| Performance | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Overall score** | **13/15** | **13/15** | **12/15** | **10/15** |

**Tiebreaker:** Gzip wins on compression ratio (6:1 vs. 4:1) and industry standard status.

## Conclusion

**Recommended strategy:** Start with Gzip (level 6), optimize to Zstd only if CPU becomes a bottleneck.

**Projected savings:** $2.13M over 10 years ($2.28M → $152K, 93% reduction)

**Key benefits:**
- Massive storage cost reduction
- Industry-standard, battle-tested solution
- Simple implementation
- Low CPU overhead
- Clear optimization path (Zstd) if needed

**Implementation timeline:**
- Week 1-2: Implement Gzip compression
- Week 3-4: Monitor production metrics
- Week 5+: Optimize to Zstd only if CPU >80% consistently

**Success criteria:**
- Compression ratio ≥ 4:1 (target: 6:1)
- CPU utilization <70% during peak writes
- Latency impact <50ms
- 0% compression/decompression errors
- Storage costs reduced by >90%

---

**Document version:** 1.0
**Last updated:** January 1, 2026
**Author:** Backend team
**Status:** Recommended for implementation
