# Caching Strategy and Cost Control

## Read cache layers

Client
 → CDN (immutable snapshots)
   → Object cache (Redis / Memcached)
     → S3

S3 snapshots are CDN-cacheable indefinitely

Latest revision pointer is cached in Redis

Vitess queries are minimized

---

## Cache invalidation

Snapshots are immutable → no invalidation needed

Head pointer cache is updated on successful write

TTL-based fallback ensures correctness
