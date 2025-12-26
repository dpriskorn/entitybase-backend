# Schema Evolution Strategy

## Embedded schema versioning

Each snapshot contains:

{
  "schema_version": "2.1",
  "entity": { ... }
}

---

## Backward compatibility rules

Readers must support N-1 schema versions

New writers emit only the latest schema

Incompatible changes require:
- New schema version
- Reader upgrade before writer rollout

---

## Migration approach

No in-place mutation of snapshots

Optional background rewrite:
- Read old snapshot
- Write new snapshot version
- Advance head pointer

History remains intact.
