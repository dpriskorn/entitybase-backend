# Storage Cost Estimations

## Overview

This document estimates storage costs for maintaining the Wikidata entity repository under the community's requirement to **keep all entity revisions indefinitely** with no expiration.

## Executive Summary

**Target scale:** 1 billion entities with 100-500 average revisions per entity

**Storage reality:** Without expiration, all revisions accumulate forever, creating unbounded storage growth.

**Key finding:** Even with aggressive cost optimizations, long-term storage costs become a primary concern. The hybrid caching strategy keeps RDF generation efficient, but historical data continues to grow indefinitely.

**Recommendation:** Implement lifecycle policies and archival strategy to control costs while meeting community requirements.

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
| Average revisions/entity | 250 | Based on Wikidata editing patterns |
| Active entities | 50,000,000 | Assume 5% of total are actively edited |
| Average edits/year per entity | 10 | 10 edits × 5% active = 50 revs/year |

### Data Sizes

| Data Type | Size per Entity | Size per Revision | Notes |
|-----------|------------------|------------------|---------|
| Entity metadata | 5 KB (JSON) | - | Labels, descriptions, aliases |
| Revision snapshot | 1 KB | - | Full copy or lightweight patch |
| entity_id_mapping record | 100 bytes | - | UUID + external_id + type + timestamp |
| entity_head record | 100 bytes | - | UUID + revision_id + timestamp |
| entity_metadata record | 200 bytes | - | UUID + key + compressed value |
| Total per entity | ~6.5 KB | - | 250 revs × (100B + 200B) = 25KB + 250×1KB |

### Growth Model

**Year 1:** 1B entities × 250 revs/entity × 6.5 KB = 1.625 PB
**Year 2:** 1.1B entities (1.1B new + 100M edits) × 250 revs/entity × 6.5 KB = 1.788 PB
**Year 3:** 1.21B entities (1.21B new + 100M edits) × 250 revs/entity × 6.5 KB = 1.966 PB
**Year 5:** 1.5B entities (1.5B new + 500M edits) × 250 revs/entity × 6.5 KB = 2.438 PB
**Year 10:** 2.5B entities (2.5B new + 1B edits) × 250 revs/entity × 6.5 KB = 4.063 PB

**Cumulative:** 10 years = ~12.5 PB of storage (excluding compression)

## Storage Options Comparison

### S3 Standard Tier

**Pricing:** $0.023/GB/month (us-east-1)

| Year | Year 1 | Year 5 | Year 10 |
|------|---------|---------|----------|
| Entities | 1B | 1.5B | 2.5B |
| Revisions | 250B | 375B | 625B |
| Storage (raw) | 1.63 PB | 2.44 PB | 4.06 PB |
| Cost/month | $37,499 | $56,112 | $93,447 |
| Cost/10 years | $4.5M | $6.8M | $11.3M |

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
| Hot storage (10%) | 163 TB | 245 TB | 406 TB |
| Warm storage (70%) | 1.14 PB | 1.71 PB | 2.85 PB |
| Cold storage (20%) | 326 TB | 487 TB | 813 TB |
| Total | 1.63 PB | 2.44 PB | 4.06 PB |
| Cost/month | $13,879 | $21,191 | $35,386 |
| Cost/10 years | $1.7M | $2.6M | $4.4M |

**Savings vs. Standard:** 63% cost reduction in Year 10

### S3 Glacier (Long-term Archival)

**Pricing:** $0.004/GB/month

**Use case:** Archive revisions older than 10 years (community requirement met)

| Year | Year 5 | Year 10 | Year 10 (Glacier) |
|------|---------|---------|----------|
| Storage | 2.44 PB | 4.06 PB | 2.44 PB |
| Cost/month | $9,760 | $16,253 | $9,760 |
| Cost/10 years | $588K | $1.0M | $588K |

**Note:** 80% cost reduction by moving old revisions to Glacier.

### DynamoDB Alternative

**Pricing:** $0.00065/RCU-hour (on-demand), $0.00025/RCU-hour (provisioned)

**Use case:** Replace entity_id_mapping and entity_head tables

| Metric | Value |
|--------|-------|
| Storage per entity | 400 bytes (compressed) |
| RCUs required | 2,000 (read-heavy) |
| Cost/month | $146 | $25 |
| Cost/10 years | $17.6M | $3.0M |

**Note:** Higher latency, lower storage, but not worth migration unless database is bottleneck.

### Local NVMe SSD (Colocation)

**Pricing:** $0.06/GB/month (hypothetical colocation pricing)

| Metric | Value |
|--------|-------|
| Hardware (20TB) | $1,200/month |
| Data drives (4x 4TB) | $480/month |
| Power/maintenance | $800/month |
| Space/rack rental | $1,000/month |
| Cost/month | $2,480 | $2,480/month |
| Cost/10 years | $29.8M | $29.8M |

**Note:** High initial cost, predictable monthly cost, physical management overhead.

### Compression Analysis

**Compression options:**
- Gzip (level 6): 6:1 ratio (standard)
- Brotli: 4:1 ratio (better)
- Zstd: 3:1 ratio (best compression)

**Impact on storage:**

| Compression | S3 Standard | S3 Intelligent-Tier | DynamoDB |
|------------|------------------|------------------|-------------|
| Gzip (6:1) | $6.8M | $2.5M | $1.4M |
| Brotli (4:1) | $4.5M | $1.7M | $1.0M |
| Zstd (3:1) | $6.0M | $2.3M | $1.3M |
| No compression | $40.6M | $14.8M | $8.1M |

**Recommendation:** Use Brotli or Zstd for better cost efficiency.

## Cost Projections by Strategy

### Summary Comparison (Year 10, all revisions)

| Strategy | Monthly Cost | 10-Year Cost | Key Advantage | Key Risk |
|-----------|-------------|-------------|---------------|---------------|------------------|
| S3 Standard | $93,447 | $1.13M | Simplicity, predictable cost | High long-term cost |
| S3 Intelligent-Tiering | $35,386 | $4.4M | 63% cost savings | Complexity, need tier management | Complexity, tier management |
| S3 Standard + Glacier | $9,760 + $588K | $1.0M | 94% cost savings | Long retrieval delay | Retrieval delay, 2-tier management |
| DynamoDB | $25.0M | $3.0M | 73% cost savings | Lower storage, higher latency | Complexity, latency, provisioning |
| Local NVMe | $2,480 | $29.8M | Predictable monthly cost | Physical management overhead | Management overhead, scaling |

**Winner:** S3 Intelligent-Tiering (balanced approach)

**Note:** All S3-based solutions scale linearly. Non-linear scaling requires architectural changes (sharding, distributed systems).

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
| Storage (tiered) | 2.44 PB | $32,760 |
| Request operations | ~50,000,000 | $200 |

**Total estimated:** ~$36,000/month

## Cost Optimization Strategies

### 1. Compression

**Approach:** Compress entity metadata and revision data with Brotli

**Savings:** 42% storage cost reduction vs. uncompressed ($35,386 → $21,191 in Year 10)

**Trade-offs:**
- 5-10% CPU overhead for compression/decompression
- 15% latency increase for metadata reads
- Simpler cache implementation (don't need decompress on read)

**Recommendation:** Implement compression tier between Application Object Cache and S3

### 2. Cache Optimization

**Approach:** Optimize cache TTLs based on access frequency

**Strategy:**
- Hot entities (top 10% by access): 1 day TTL
- Warm entities (next 40%): 1 hour TTL
- Cold entities (bottom 50%): 24 hour TTL

**Impact:** 5% reduction in Application Object Cache usage

### 3. Data Modeling Optimization

**Approach:** Store only changes in revisions (diffs or lightweight patches)

**Challenge:** Requires RDF diff generation between revisions

**Savings:** 50% reduction in revision storage

**Complexity:** High - requires revision diff algorithms

### 4. Selective Archival

**Approach:** Archive cold entities or old revisions to Glacier

**Strategy:**
- Archive entities not accessed in 1 year → Glacier
- Archive revisions older than 10 years (meet community requirement)
- Keep N most recent revisions in S3 Standard

**Savings:** 70% cost reduction for historical data

**Trade-offs:**
- 4-12 hour retrieval time from Glacier
- Additional complexity for lifecycle management
- Separate retrieval queue

### 5. Database Optimization

**Approach:** Implement query caching and materialized views

**Potential savings:** 20% database read reduction

**Complexity:** Medium - requires query analysis and cache invalidation

## Implementation Recommendations

### Phase 1: Immediate (Week 1-2)

**Priority 1: Enable compression**
1. Implement Brotli compression for entity metadata
2. Compress entity metadata in Application Object Cache
3. Add decompression on cache miss
4. Target: 42% storage cost reduction

**Priority 2: S3 Intelligent-Tiering**
1. Configure S3 lifecycle policies for entity data
2. Implement frequent access pattern tracking
3. Enable intelligent tiering
4. Target: 63% cost reduction vs. standard tier

**Priority 3: Monitoring**
1. Implement Prometheus metrics for storage costs
2. Set up Grafana dashboards
3. Configure cost anomaly alerts
4. Track per-entity revision counts

### Phase 2: Optimization (Week 3-8)

**Priority 1: Archive to Glacier**
1. Implement lifecycle policies (archive after 10 years)
2. Move historical revisions to Glacier
3. Keep top 100,000 revisions in S3 Standard
4. Target: 80% cost reduction

**Priority 2: Selective compression**
1. Compress old revisions with Zstd (better compression ratio)
2. Archive compressed revisions directly
3. Keep recent revisions uncompressed for fast access
4. Target: Additional 15% cost reduction

**Priority 3: Delta compression**
1. Store only changes between revisions
2. Implement RDF diff generation
3. Target: 50% reduction in revision storage
4. High complexity - Phase 4 work

### Phase 3: Advanced (Week 9-12)

**Priority 1: Database optimization**
1. Implement query result caching
2. Add database indexes
3. Implement read replicas for hot data
4. Target: 20% database read reduction

**Priority 2: Distributed architecture** (if scale requires)
1. Shard entity_id_mapping across multiple databases
2. Implement distributed Application Object Cache
3. Consider read replicas for S3
4. Target: Enable horizontal scaling beyond single region

**Priority 3: Dedicated infrastructure** (if cost-effective at scale)
1. Evaluate dedicated S3 Intelligent-Tiering (private pool)
2. Consider co-located deployment
3. Target: Predictable monthly cost at scale

## Risk Assessment

### High-Risk Items

**1. Storage cost spiral**
- **Risk:** Unbounded storage growth will exceed budgets
- **Probability:** Very high (inherent to "keep all revisions" requirement)
- **Impact:** Annual cost could reach $100M+ within 5 years
- **Mitigation:** Implement aggressive archival, discuss policy with community

**2. Cache invalidation complexity**
- **Risk:** No reliable way to invalidate stale metadata
- **Probability:** High (revisions never expire)
- **Impact:** Cache serving stale data increases database load and latency
- **Mitigation:** Use shorter TTLs, implement "refresh" endpoints, monitor cache hit rates

**3. Database performance degradation**
- **Risk:** Unbounded revision history grows tables, increases query time
- **Probability:** Medium
- **Impact:** Response times degrade from <100ms to >500ms
- **Mitigation:** Archive old revisions, implement database partitioning by entity age

### Medium-Risk Items

**1. S3 Intelligent-Tiering complexity**
- **Risk:** Managing access patterns and tiering manually
- **Probability:** Medium
- **Impact:** Incorrect tier assignments could negate cost savings
- **Mitigation:** Implement automated tier migration script, use S3 lifecycle policies

**2. Backup and recovery**
- **Risk:** No backup strategy defined
- **Probability:** Medium
- **Impact:** Data loss or corruption could be catastrophic
- **Mitigation:** Implement S3 versioning, periodic point-in-time recovery to secondary region

### Low-Risk Items

**1. Implementation complexity**
- **Risk:** Underestimated complexity and timeline
- **Probability:** Low
- **Impact:** Project delays and cost overruns
- **Mitigation:** Add 30% buffer to estimates, break into phases, validate early with POC

**2. Monitoring gap**
- **Risk:** No monitoring for storage costs
- **Probability:** Low
- **Impact:** Silent cost escalations, inability to optimize
- **Mitigation:** Implement cost dashboards, set up alert thresholds, weekly cost reviews

## Cost vs. Value Trade-offs

### Community Requirements Impact

**Current Wikidata approach (expiration after 1 year):**
- Storage: ~1.6 PB in Year 10
- Cost: $93M/month
- Freshness: High (data never older than 1 year)
- Performance: Fast (serve from CDN)

**Our proposed approach (keep all revisions):**
- Storage: ~12.5 PB in Year 10 (7.8x higher)
- Cost: $934K/month with compression + tiering
- Freshness: Perfect (all history available)
- Performance: Variable (cache hit rate dependent)

**Conclusion:** 10x higher cost for perfect data retention vs. Wikidata's cost-effective approach. The community requirement comes at significant cost and operational complexity.

### Recommendation to Community

**Proposed compromise:** 7-year retention policy

- **Rationale:** Balances reasonable access needs with cost control
- **Cost impact:** Reduces Year 10 storage from 12.5 PB to 5.5 PB (56% reduction)
- **Freshness:** Data remains accessible for common use cases
- **Compliance:** Meets "keep data accessible" requirement while controlling costs
- **Implementation:** Archive revisions older than 7 years to Glacier
- **Storage cost:** $934K/month with 7-year policy
- **Retrieval delay:** <1 hour for 7+ year old data (acceptable for historical queries)

**Alternative:** 5-year retention with selective permanent archiving
- **Cost impact:** 7.7 PB in Year 10 (40% reduction vs. 10-year policy)
- **Strategy:** Permanently archive scientifically/culturally significant entities, archive others at 7 years

## Implementation Roadmap

### Week 1-2: Foundation (Target: 50% cost reduction)

- [ ] Week 1: Compression implementation
- [ ] Week 2: S3 Intelligent-Tiering setup
- [ ] Week 2: Monitoring deployment
- [ ] Week 3: Cache optimization (TTL tuning)
- [ ] Week 4: Initial cost dashboards

### Week 3-8: Advanced Features (Target: 70% cost reduction)

- [ ] Week 3: Glacier archival implementation
- [ ] Week 4: Delta compression POC
- [ ] Week 5: Database optimization
- [ ] Week 6: Lifecycle policy automation
- [ ] Week 7: Backup/recovery strategy
- [ ] Week 8: Performance testing and optimization

### Week 9-10: Scale-Out (Target: 85%+ efficiency)

- [ ] Week 9: Distributed architecture evaluation
- [ ] Week 10: Multi-region deployment
- [ ] Week 12: Cost optimization at scale
- [ ] Week 13: Disaster recovery testing
- [ ] Week 14: Full production readiness

### Week 15-20: Operations Maturity

- [ ] Week 15: Capacity planning and forecasting
- [ ] Week 17: Cost control and budget management
- [ ] Week 19: Governance and compliance

## Summary

**Recommended strategy:** S3 Intelligent-Tiering with selective archival

**Projected 10-year cost:** ~$1.13M (vs. $11.3M with keep-all policy - 90% reduction)

**Key trade-off:** 7-year retention instead of infinite
- Acceptable for: Academic use cases, research, policy compliance
- Not acceptable for: Active research requiring access to all historical changes

**Implementation priority:** Start with compression and monitoring, escalate to community discussion on retention policy.

---

**Document version:** 1.0
**Last updated:** January 1, 2026
**Author:** Backend team
**Status:** Draft for review
