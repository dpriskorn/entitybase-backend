# Weekly RDF Dump Cost Estimation

## Overview

This document estimates the cost of generating and storing weekly RDF dumps for the Wikibase knowledge base. Weekly dumps provide complete snapshots for archival, distribution, and bulk import purposes.

**Important Note:** All calculations use AWS S3 pricing for estimates. Expect at least 10% overhead when running on Wikimedia Foundation (WMF) infrastructure due to additional operational costs, internal services, and compliance requirements.

## Executive Summary

**Weekly dump strategy:** Generate JSON and RDF/Turtle dumps weekly, retain for 1 year in S3, transfer to Internet Archive for permanent storage

**Key findings:**
- Weekly dump size: 7.05 TB compressed (JSON + RDF)
- Annual S3 storage cost: ~$23,738
- Annual Internet Archive transfer cost: ~$7,340
- Total annual cost: ~$31,078 (plus 10% WMF overhead = ~$34,186)
- 10-year cost: ~$310,780 (plus 10% WMF overhead = ~$341,858)

**Comparison to baseline:** Weekly dump costs are ~1.5% of baseline S3 storage costs ($2.28M/year at Year 10)

## Data Model

### Empirical Measurements

Based on empirical data from 300 entity samples:

| Parameter | Value | Source |
|-----------|-------|--------|
| Mean entity size | 16.9 KB | scripts/size_estimation.txt |
| Mean revisions per entity | 20 | scripts/revision_count_estimation.txt |
| RDF/JSON size ratio | 1.5x | Industry standard |
| Gzip compression ratio | 6:1 | doc/OPTIMIZATIONS/COMPRESSION.md |

### Weekly Dump Composition

Weekly dumps contain **current revisions only** (standard practice), not full revision history.

**Assumptions:**
- Target scale: 1 billion entities
- Weekly dumps generate both JSON and RDF (Turtle) formats
- Dumps use Gzip compression
- All entities included in each weekly dump (incremental dumps not considered)

## Dump Size Estimation

### Uncompressed Weekly Dump

**JSON dump (1B entities):**
```
16.9 KB/entity × 1,000,000,000 entities = 16.9 TB
```

**RDF dump (1B entities):**
```
16.9 KB × 1.5 (RDF expansion) × 1,000,000,000 entities = 25.4 TB
```

**Total uncompressed:**
```
16.9 TB + 25.4 TB = 42.3 TB
```

### Compressed Weekly Dump (Gzip, 6:1 ratio)

**JSON dump (compressed):**
```
16.9 TB ÷ 6 = 2.82 TB
```

**RDF dump (compressed):**
```
25.4 TB ÷ 6 = 4.23 TB
```

**Total compressed:**
```
2.82 TB + 4.23 TB = 7.05 TB
```

### Per-Entity Breakdown

| Component | Uncompressed | Compressed | Compression Ratio |
|-----------|-------------|-------------|-------------------|
| JSON entity | 16.9 KB | 2.82 KB | 6:1 |
| RDF entity | 25.4 KB | 4.23 KB | 6:1 |
| Total per entity | 42.3 KB | 7.05 KB | 6:1 |

## S3 Storage Cost Analysis

### Retention Policy

**Lifecycle strategy:**
- 0-30 days: S3 Standard ($0.023/GB)
- 30-90 days: S3 Standard-IA ($0.0125/GB)
- 90-180 days: S3 Glacier ($0.004/GB)
- 180-365 days: S3 Glacier Deep Archive ($0.00099/GB)
- 365+ days: Transfer to Internet Archive, delete from S3

### Steady-State Storage (52 weeks)

Weekly dump generation at 1B entity scale:

**Weekly additions:** 7.05 TB

**Distribution across retention tiers:**

| Tier | Duration | Weeks | Storage | Monthly Cost |
|------|-----------|--------|---------|--------------|
| Standard | 0-30 days | 4 | 28.2 TB | $644 |
| Standard-IA | 30-90 days | 8 | 56.4 TB | $702 |
| Glacier | 90-180 days | 12 | 84.6 TB | $338 |
| Deep Archive | 180-365 days | 26 | 183.3 TB | $182 |
| **Total** | 365 days | **52** | **352.5 TB** | **$1,866** |

**Note:** Standard-IA period reduced from 9 to 8 weeks to align with 30-90 day window accurately.

### Annual S3 Storage Cost

**Monthly calculation:**
```
$644 (Standard) + $702 (Standard-IA) + $338 (Glacier) + $182 (Deep Archive)
= $1,866/month
```

**Annual cost:**
```
$1,866/month × 12 months = $22,392/year
```

### S3 Request Costs

**Weekly operations:**

| Operation | Count | Cost per 1K | Weekly Cost | Annual Cost |
|-----------|--------|--------------|-------------|-------------|
| PUT (upload) | 2 (JSON, RDF) | $0.005 | $0.01 | $0.52 |
| GET (verification) | 2 | $0.0004 | $0.0008 | $0.04 |
| Lifecycle transitions | 52 | Included | $0 | $1.56 |
| **Total** | - | - | **$0.01** | **$2.12** |

**Total S3 annual cost:**
```
$22,392 (storage) + $2.12 (requests) = $22,394/year
```

## Internet Archive Transfer Costs

### Transfer Volume

**Weekly transfer to Internet Archive:**
```
7.05 TB/week × 52 weeks/year = 366.6 TB/year
```

### S3 Egress Costs

**S3 to Internet Archive bandwidth:**
- S3 egress pricing: ~$0.02/GB (standard)
- Annual transfer cost:
```
366.6 TB × 1024 GB/TB × $0.02/GB = $7,508/year
```

### Total Annual Cost

**S3 storage and requests:**
```
$22,394/year
```

**S3 egress to Internet Archive:**
```
$7,508/year
```

**Total annual cost:**
```
$22,394 + $7,508 = $29,902/year
```

## WMF Infrastructure Overhead

**Required overhead: Minimum 10%**

**Reasons for overhead:**
- Internal network infrastructure
- Operational support and monitoring
- Compliance and security requirements
- Redundancy and backup systems
- Shared infrastructure costs

**Annual cost with 10% overhead:**
```
$29,902 × 1.10 = $32,892/year
```

## 10-Year Cost Projection

### S3 Storage Costs (constant each year)

**Annual S3 cost:**
```
$22,394/year
```

**10-year S3 cost:**
```
$22,394 × 10 = $223,940
```

### Internet Archive Transfer Costs (constant each year)

**Annual transfer cost:**
```
$7,508/year
```

**10-year transfer cost:**
```
$7,508 × 10 = $75,080
```

### Total 10-Year Cost

**10-year total (AWS S3 pricing):**
```
$223,940 (S3) + $75,080 (transfer) = $299,020
```

**10-year total (with 10% WMF overhead):**
```
$299,020 × 1.10 = $328,922
```

## Cost Comparison

### Baseline Storage Costs

From STORAGE-COST-ESTIMATIONS.md:

| Scale | Monthly Storage Cost | Annual Storage Cost |
|-------|-------------------|-------------------|
| Year 1 (1B entities) | $7,594 | $91,128 |
| Year 5 (1.5B entities) | $11,391 | $136,692 |
| Year 10 (2.5B entities) | $18,986 | $227,832 |

### Weekly Dump vs. Baseline

**At Year 10 scale (2.5B entities):**

| Cost Component | Annual Cost |
|---------------|-------------|
| Baseline S3 storage | $227,832 |
| Weekly dumps (AWS) | $29,902 |
| Weekly dumps (WMF +10%) | $32,892 |
| **Weekly dump % of baseline** | **13.1% (AWS), 14.4% (WMF)** |

**Conclusion:** Weekly dump costs represent ~14% of baseline S3 storage costs at Year 10 scale.

## Alternative Scenarios

### Scenario 1: No Internet Archive Partnership

**Retain all dumps in S3 indefinitely:**

**Storage growth:**
```
7.05 TB/week × 52 weeks/year = 366.6 TB/year
Year 10 cumulative: 3.67 PB
```

**Cost projection (Year 10):**
- Monthly: ~$70,000
- Annual: ~$840,000
- **Cost increase:** 2.5x vs. Internet Archive strategy

**Recommendation:** Internet Archive partnership is highly cost-effective.

### Scenario 2: Alternative Retention Periods

**6-month retention (instead of 1 year):**

**Storage:** 52 weeks → 26 weeks
- S3 storage cost: $11,000/year
- IA transfer cost: $3,750/year
- Total: $14,750/year (51% reduction)

**Trade-off:** Less archival redundancy, community pushback expected

**Recommendation:** Keep 1-year retention for community trust.

### Scenario 3: Monthly Dumps (instead of weekly)

**Monthly dump size:**
```
7.05 TB/week × 4 = 28.2 TB/month
```

**Annual cost:**
- S3 storage: $6,000/year
- IA transfer: $1,875/year
- Total: $7,875/year (74% reduction)

**Trade-off:** Less frequent snapshots, stale data for bulk imports

**Recommendation:** Weekly dumps balance cost and data freshness.

## Cost Optimization Strategies

### 1. Compression Level Optimization

**Current:** Gzip level 6 (6:1 ratio)

**Alternative:** Zstd level 3 (4:1 ratio, faster)

**Impact:**
- S3 storage: +50% (4:1 vs 6:1)
- CPU overhead: -50% (faster compression)
- Net cost impact: +$11,000/year S3, -$500 CPU

**Recommendation:** Stick with Gzip level 6 for optimal cost.

### 2. Differential Dumps

**Strategy:** Store full dump monthly, generate differential dumps weekly

**Impact:**
- Weekly diff size: ~5-10% of full dump
- Storage reduction: ~90%
- Complexity: High (diff generation, merging)

**Recommendation:** Not worth complexity given manageable baseline costs.

### 3. Deduplication

**Strategy:** Deduplicate common data across dumps (labels, descriptions)

**Impact:**
- Potential savings: 20-30% storage
- Complexity: High (requires custom indexing)
- Retrieval complexity: High

**Recommendation:** Not recommended for initial implementation.

## Implementation Costs

### Infrastructure Requirements

**Compute resources (weekly job):**
- CPU: 4-8 cores for conversion
- Memory: 8-16 GB for processing
- Storage: 50 GB temporary (for dumps)
- Duration: 2-6 hours per run

**Annual compute cost:**
- Weekly job: 4 hours × 52 = 208 hours/year
- Spot instance cost: ~$0.05/hour
- **Annual compute: ~$10**

**Negligible compared to storage costs.**

### Development Costs

**Estimated effort:**
- Development: 2-3 weeks
- Testing: 1 week
- Integration: 1 week
- Total: 4-5 weeks

**One-time cost:** Not included in ongoing operational estimates.

## Risk Assessment

### High-Risk Items

**1. Internet Archive partnership changes**
- **Risk:** Internet Archive changes terms or accepts fewer dumps
- **Probability:** Low
- **Impact:** Medium (need alternative archival strategy)
- **Mitigation:** Multiple archival options, monitor IA status

### Medium-Risk Items

**1. Transfer cost increases**
- **Risk:** S3 egress pricing increases
- **Probability:** Medium (historical trend)
- **Impact:** Medium (cost increase from $7.5K/year)
- **Mitigation:** Negotiate enterprise rates, consider alternative archival

**2. Dump generation failures**
- **Risk:** Weekly job fails, skips dump
- **Probability:** Medium
- **Impact:** Low (single week missing from archive)
- **Mitigation:** Retry logic, alerting, manual rerun capability

### Low-Risk Items

**1. Storage cost increases**
- **Risk:** S3 pricing increases
- **Probability:** Low
- **Impact:** Low (manageable cost scale)
- **Mitigation:** Intelligent-Tiering, compression optimizations

**2. WMF overhead higher than expected**
- **Risk:** Overhead exceeds 10%
- **Probability:** Low
- **Impact:** Low (still manageable at 20% overhead)
- **Mitigation:** Monitor actual costs, adjust projections

## Monitoring and Metrics

### Key Metrics to Track

**Storage metrics:**
- Weekly dump size (JSON and RDF)
- S3 storage per tier
- Internet Archive transfer volume
- Compression ratio achieved

**Cost metrics:**
- S3 storage cost per month
- S3 request costs
- S3 egress costs to Internet Archive
- WMF infrastructure overhead

**Operational metrics:**
- Dump generation duration
- Transfer success rate
- Failed transfer retries
- API availability

### Alerting Thresholds

**Cost alerts:**
- S3 monthly cost > $2,000
- Annual transfer cost > $8,000
- WMF overhead > 15%

**Operational alerts:**
- Dump generation time > 8 hours
- Transfer failure rate > 5%
- Weekly dump skipped

## Recommendations

### Primary Recommendation

**Implement weekly dumps with 1-year S3 retention + Internet Archive archival**

**Key benefits:**
- Manageable annual cost: ~$33K (including WMF overhead)
- Community alignment with Wikidata's approach
- Permanent archival via Internet Archive
- Regular snapshots for bulk imports
- Data provenance and historical tracking

### Secondary Recommendations

1. **Start with Gzip compression:** Optimize to Zstd only if CPU becomes bottleneck
2. **Monitor Internet Archive health:** Establish secondary archival option if needed
3. **Track actual WMF overhead:** Adjust projections after 6-12 months of data
4. **Consider incremental dumps:** Evaluate if monthly full + weekly diff makes sense at scale
5. **Community consultation:** Confirm 1-year retention meets community needs

### Implementation Priority

**Phase 1 (Immediate):**
- Implement weekly dump generation
- Configure S3 lifecycle rules
- Establish Internet Archive transfer automation

**Phase 2 (Months 1-3):**
- Monitor and optimize performance
- Track actual costs vs. estimates
- Refine compression settings if needed

**Phase 3 (Months 3-12):**
- Evaluate incremental dump approach
- Assess WMF overhead accuracy
- Consider archival strategy diversification

## Summary

**Total annual cost:** ~$32,892 (AWS pricing + 10% WMF overhead)
**10-year cost:** ~$328,922
**Cost relative to baseline:** ~14% of S3 storage costs at Year 10 scale

**Conclusion:** Weekly RDF dump generation is cost-effective and aligned with community expectations for a Wikibase knowledge base. The combination of S3 tiered storage and Internet Archive archival provides optimal balance of cost, accessibility, and permanence.

---

**Document version:** 1.0
**Last updated:** January 1, 2026
**Author:** Backend team
**Status:** Draft for review

**Related documents:**
- STORAGE-COST-ESTIMATIONS.md - Baseline storage cost analysis
- COMPRESSION.md - Compression strategy recommendations
- WEEKLY-RDF-DUMP-GENERATOR.md - Implementation architecture
