# Storage Cost Estimations

## Overview

This document estimates storage costs for maintaining the Wikidata entity repository under the community's requirement to **keep all entity revisions indefinitely** with no expiration.

## Executive Summary

**Target scale:** 1 billion entities

**Storage reality:** Without expiration, all revisions accumulate forever, creating unbounded storage growth.

**Key finding:** Empirical data from 300 entity samples shows storage costs are manageable ($2.28M over 10 years at scale, or $227K with compression).

**Recommendation:** Use S3 Standard with compression. Add archival only if costs increase at scale.

## Scope

**What's included:**
- Entity metadata storage (labels, descriptions, aliases, sitelinks)
- Entity revision history (full copies or snapshots)
- Database storage (entity_id_mapping, entity_head, entity_metadata)
- Referenced entity data
- Property metadata

**What's NOT included:**
- Generated RDF (generated on-demand, not stored)
- Application cache layers (Application Object Cache, CDN)
- S3 object storage for generated snapshots (separate system)

## Baseline Assumptions

### Entity Activity

| Parameter | Assumption | Rationale |
|-----------|------------|-----------|
| Total entities | 1,000,000,000 | Target scale for 2025 |
| New entities/year | 100,000,000 | Current growth rate (Wikidata scale) |
| Average revisions/entity | 20 | Empirical mean from sample (n=300, stdev: 28) |

### Data Sizes

| Data Type | Size per Entity | Notes |
|-----------|------------------|---------|
| All revisions (20 avg) | 329.8 KB | 20 revisions × 16.5 KB (empirical mean) |
| Database records | 0.4 KB | entity_id_mapping + entity_head + entity_metadata |
| Total per entity | ~330.2 KB | All data including full revision history |

### Growth Model

**Year 1:** 1B entities × 330.2 KB = 330.2 TB
**Year 2:** 1.1B entities × 330.2 KB = 363.2 TB
**Year 3:** 1.21B entities × 330.2 KB = 399.5 TB
**Year 5:** 1.5B entities × 330.2 KB = 495.3 TB
**Year 10:** 2.5B entities × 330.2 KB = 825.5 TB

**Cumulative:** 10 years = ~2.6 PB of storage (excluding compression)

## Storage Options Comparison

### S3 Standard Tier

**Pricing:** $0.023/GB/month (us-east-1)

| Year | Year 1 | Year 5 | Year 10 |
|------|---------|---------|----------|
| Entities | 1B | 1.5B | 2.5B |
| Revisions | 20B | 30B | 50B |
| Storage (raw) | 330.2 TB | 495.3 TB | 825.5 TB |
| Cost/month | $7,594 | $11,391 | $18,986 |
| Cost/10 years | $911K | $1.37M | $2.28M |

### S3 Intelligent-Tiering

**Pricing:**
- Frequent Access: $0.01/GB (first 50TB/month)
- Infrequent Access: $0.0075/GB (next 100TB/month)
- Archive Access: $0.004/GB (remaining storage)

**Assumptions:**
- 10% hot (frequent), 70% warm (infrequent), 20% cold (archive)
- 90% of reads hit hot tier

| Year | Year 1 | Year 5 | Year 10 |
|------|---------|---------|----------|
| Total storage | 330.2 TB | 495.3 TB | 825.5 TB |
| Cost/month | $2,357 | $3,565 | $5,953 |
| Cost/10 years | $283K | $428K | $714K |

### S3 Glacier (Long-term Archival)

**Pricing:** $0.004/GB/month

**Use case:** Archive revisions older than 10 years

| Year | Year 5 | Year 10 | Year 10 (Glacier) |
|------|---------|---------|----------|
| Storage | 495.3 TB | 825.5 TB | 495.3 TB |
| Cost/month | $1,981 | $3,302 | $1,981 |
| Cost/10 years | $238K | $396K | $238K |



### Local NVMe SSD (Colocation)

**Pricing:** $0.06/GB/month (hypothetical colocation pricing)

| Metric | Value |
|--------|-------|
| Hardware (20TB) | $1,200/month |
| Data drives (4x 4TB) | $480/month |
| Power/maintenance | $800/month |
| Space/rack rental | $1,000/month |
| Cost/month | $2,480 |
| Cost/10 years | $29.8M |

**Note:** High initial cost, predictable monthly cost, physical management overhead.

### Compression Analysis

**Compression options:**
- Gzip (level 6): 6:1 ratio (standard)
- Brotli: 4:1 ratio (better)
- Zstd: 3:1 ratio (best compression)

**Impact on storage:**

| Compression | S3 Standard | S3 Intelligent-Tier |
|------------|------------------|------------------|
| Gzip (6:1) | $152K | $47K |
| Brotli (4:1) | $227K | $71K |
| Zstd (3:1) | $303K | $95K |
| No compression | $2.28M | $714K |

## Cost Projections by Strategy

### Summary Comparison (Year 10, all revisions)

| Strategy | Monthly Cost | 10-Year Cost | Key Advantage |
|-----------|-------------|-------------|---------------|
| S3 Standard | $18,986 | $2.28M | Simplicity, predictable cost |
| S3 Intelligent-Tiering | $5,953 | $714K | 69% cost savings |
| S3 Standard + Glacier | $1,981 | $238K | 90% cost savings |
| Local NVMe | $2,480 | $29.8M | Predictable monthly cost |

**Winner:** S3 Standard (simplest approach with low cost)

**Note:** All S3-based solutions scale linearly.

## Operational Cost Analysis

### S3 Request Costs

| Operation | Cost | Monthly operations | Notes |
|-----------|------|------------------|------------------|
| GET (data retrieval) | $0.0004/1000 requests | Entity metadata lookups |
| PUT (entity updates) | $0.005/1000 requests | Entity creation/updates |
| S3 Intelligent-Tiering | Included in tier pricing | Frequent reads penalized |
| Lifecycle operations (tags) | Included | Revision management tags |

### Estimated Monthly Operations (S3 Intelligent-Tiering, Year 10)

| Metric | Count | Cost |
|--------|-------|------|--------|
| Entity metadata reads | 50,000,000 entities × 12 reads/month | $2,400 |
| Entity updates | 100,000,000 entities × 1 update/month | $500 |
| Revision reads (entity_head) | 50B entities × 12 reads/month | $0.02 |
| Storage (tiered) | 825.5 TB | $5,953 |
| Request operations | ~50,000,000 | $200 |

**Total estimated:** ~$9,053/month

## Cost Optimization Strategies

### 1. Compression

**Approach:** Compress entity metadata and revision data with Brotli

**Savings:** 90% storage cost reduction vs. uncompressed ($7,986 → $798 in Year 10)

**Trade-offs:**
- 5-10% CPU overhead for compression/decompression
- 15% latency increase for metadata reads

### 2. Selective Archival

**Approach:** Archive cold entities or old revisions to Glacier

**Strategy:**
- Archive revisions older than 10 years
- Keep N most recent revisions in S3 Standard

**Savings:** 60% cost reduction for historical data

**Trade-offs:**
- 4-12 hour retrieval time from Glacier
- Additional complexity for lifecycle management

## Implementation Recommendations

### Phase 1: Initial (Week 1-2)

**Priority 1: Start with S3 Standard**
1. Implement basic S3 storage for entities
2. Store full revision history
3. Target: $19K/month at Year 10 scale

**Priority 2: Monitoring**
1. Implement Prometheus metrics for storage costs
2. Set up Grafana dashboards
3. Configure cost anomaly alerts
4. Track per-entity revision counts

### Phase 2: Optimization (Week 3-8)

**Priority 1: Compression**
1. Implement Brotli compression for entity metadata
2. Compress historical revisions
3. Target: 90% storage cost reduction ($2.28M → $227K over 10 years)

**Priority 2: Archive to Glacier** (if needed)
1. Implement lifecycle policies (archive after 10 years)
2. Move historical revisions to Glacier
3. Keep top 100,000 revisions in S3 Standard
4. Target: Additional 65% cost reduction

## Risk Assessment

### High-Risk Items

**1. Cache invalidation complexity**
- **Risk:** No reliable way to invalidate stale metadata
- **Probability:** High (revisions never expire)
- **Impact:** Cache serving stale data increases database load and latency
- **Mitigation:** Use shorter TTLs, implement "refresh" endpoints, monitor cache hit rates

### Medium-Risk Items

**1. Backup and recovery**
- **Risk:** No backup strategy defined
- **Probability:** Medium
- **Impact:** Data loss or corruption could be catastrophic
- **Mitigation:** Implement S3 versioning, periodic point-in-time recovery to secondary region

### Low-Risk Items

**1. Storage cost spiral**
- **Risk:** Unbounded storage growth will exceed budgets
- **Probability:** Low (empirical data shows manageable costs)
- **Impact:** Annual cost could reach $30K within 5 years
- **Mitigation:** Monitor growth trends, implement archival if needed

**2. Implementation complexity**
- **Risk:** Underestimated complexity and timeline
- **Probability:** Low
- **Impact:** Project delays and cost overruns
- **Mitigation:** Add 30% buffer to estimates, break into phases, validate early with POC

## Cost vs. Value Trade-offs

### Empirical Findings

**Based on sample of 300 entities:**
- Mean revisions: 20 (median: 13, stdev: 28)
- Mean entity size: 16.9 KB (median: 10.8 KB, stdev: 20.6 KB)
- Total per entity: ~330.2 KB (including full revision history)

**Storage costs are manageable:**
- Year 10: 825.5 TB at $19K/month (S3 Standard)
- With compression: $2.28M → $227K over 10 years (90% reduction)
- Community requirement met with compression

### Recommendation

**Keep-all-revisions with S3 Standard + Compression**

- Empirical data shows costs are manageable with compression
- Perfect data retention, all history always available
- Simple architecture, no complex lifecycle policies needed
- Storage cost: $19K/month in Year 10 (no compression), $2.3K/month with Brotli
- No retrieval delays (all data in hot tier)

**Alternative:** Add Glacier archival for further cost reduction
- Cost impact: $2.28M → $238K over 10 years (90% reduction)
- Trade-off: 4-12 hour retrieval time for historical data
- Use case: Only if costs become problematic at extreme scale

## Implementation Roadmap

### Week 1-2: Foundation

- [ ] Week 1: S3 Standard storage implementation
- [ ] Week 1: Monitoring deployment
- [ ] Week 2: Initial cost dashboards

### Week 3-8: Optimization

- [ ] Week 3: Compression implementation (Brotli)
- [ ] Week 4: Compression testing and tuning
- [ ] Week 5: Performance testing
- [ ] Week 6: Cost optimization analysis
- [ ] Week 7: Backup/recovery strategy
- [ ] Week 8: Full production readiness

### Week 9+: Operations

- [ ] Ongoing: Cost monitoring and alerts
- [ ] Ongoing: Capacity planning
- [ ] Optional: Glacier archival if costs increase
- [ ] Optional: Intelligent-Tiering if access patterns warrant

## Summary

**Recommended strategy:** S3 Standard with compression

**Projected 10-year cost:** ~$227K (or $2.28M without compression)

**Key finding:** Empirical data (mean: 20 revisions, 16.9KB entity) shows costs are manageable at scale with compression

**Implementation priority:** Start with S3 Standard + compression, add Glacier archival only if costs increase.

**Data source:** Empirical measurements from 300 entity samples (scripts/size_estimation.py, scripts/revision_count_estimation.py)

---

**Document version:** 2.0
**Last updated:** January 1, 2026
**Author:** Backend team
**Status:** Updated with empirical data from size and revision count estimation scripts
