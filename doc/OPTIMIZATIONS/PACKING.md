# Optimization Strategy: Packing and Compressing Long-Tail Statements

## Summary
This document proposes an optimization strategy for large, statement-centric knowledge bases (e.g. Wikidata) that suffer from poor scaling due to permanent history and high per-statement overhead.

The core idea is to **pack and aggressively compress long-tail statements**—statements used by very few entities (e.g. fewer than 5)—while keeping frequently used statements in a hot, normalized storage path.

This strategy targets the dominant cost drivers without compromising correctness, provenance, or permanent history.

---

## Problem Statement

### Observed issues
- Storage grows super-linearly for large, frequently edited entities
- Permanent history multiplies storage costs
- Each statement carries high structural overhead (IDs, qualifiers, references)
- Rarely used statements pay the same storage and indexing cost as common ones

In practice, this leads to **O(n × r)** storage behavior (statements × revisions), which often behaves like **O(n²)** for popular entities.

---

## Key Observation: Heavy-Tailed Distribution

Statement usage follows a heavy-tailed (Zipf-like) distribution:

- A small number of statements are used by many entities
- A very large number of statements are used by very few entities
- Rare statements tend to remain rare over time

This makes rare statements ideal candidates for:
- cold storage
- aggressive compression
- delayed materialization

---

## Proposed Strategy

### 1. Split Storage into Tiers

#### Hot Tier
For frequently used statements:
- Normalized representation
- Fully indexed
- Optimized for low-latency reads and writes
- Used by most queries and editors

#### Cold Tier (Long Tail)
For rarely used statements (e.g. used by <5 entities):
- Packed across entities
- Delta-compressed
- Dictionary-encoded
- Fewer or no secondary indexes
- Loaded lazily on demand

---

## Statement Packing

### What is a Statement Pack?
A **statement pack** groups many similar, rarely used statements into a shared storage unit.

Packs may be organized by:
- property
- value type
- time window (for history)
- or a combination thereof

### Pack Contents (Example)
- Property ID
- List of Entity IDs
- Encoded values (dictionary or columnar encoding)
- Optional qualifiers and references (compressed)
- Metadata summary (counts, min/max timestamps)

This amortizes structural overhead across many statements.

---

## Compression Techniques

- Delta compression against similar statements
- Dictionary encoding for repeated values
- Columnar layout for values and qualifiers
- Periodic repacking (Git-style) to improve compression ratios

This is conceptually similar to:
- Git packfiles
- Parquet / ORC columnar formats

---

## Access Model

1. **Normal queries**
   - Hit only the hot tier
   - No performance regression

2. **Rare queries**
   - Detect presence of cold-tier statements
   - Lazily load and materialize from packs

3. **Background processes**
   - Monitor access frequency
   - Promote warming statements to hot tier
   - Demote cooling statements to cold tier (with hysteresis)

---

## Thresholds and Hysteresis

- Initial cold threshold: <5 entities
- Promotion threshold: e.g. >10 entities
- Demotion threshold: e.g. <3 entities

This prevents flapping between tiers.

---

## Interaction with Permanent History

History can also be packed:

- Store historical edits as event streams or deltas
- Periodically rebase into full snapshots
- Pack historical revisions by property and time window

This preserves:
- full auditability
- rollback capability
- provenance guarantees

While drastically reducing storage cost.

---

## Benefits

- Reduces per-statement overhead for rare data
- Improves overall storage asymptotics
- Keeps hot paths fast and simple
- Aligns with real-world query patterns
- Compatible with permanent history

This directly attacks the cost drivers responsible for effective O(n²) behavior.

---

## Risks and Mitigations

### Query Planning Complexity
**Risk:** SPARQL engines dislike opaque blobs  
**Mitigation:** Maintain pack-level metadata and summaries

### Migration Complexity
**Risk:** Statements move between hot and cold tiers  
**Mitigation:** Background jobs + hysteresis thresholds

### Editorial UX
**Risk:** Lazy loading could confuse editors  
**Mitigation:** Make materialization transparent in UI and APIs

---

## Why This Is Hard to Retrofit
- MediaWiki’s legacy data model
- Tight coupling between storage and query layers
- Conservative correctness culture

However, architecturally, this strategy offers one of the few realistic paths to flatten the long-term cost curve.

---

## Conclusion

Packing and compressing long-tail statements is a high-leverage optimization:

- It exploits known data distributions
- It borrows proven ideas from Git and columnar storage
- It preserves Wikidata’s core values
- It meaningfully improves scalability

This approach should be considered a foundational storage optimization rather than a micro-optimization.

---
