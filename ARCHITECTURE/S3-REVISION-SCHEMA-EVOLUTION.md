# Schema Evolution Strategy

## Semantic versioning

Schema versions follow **semantic versioning**: `MAJOR.MINOR`

- **MAJOR** (e.g., 1.0, 2.0): Incompatible, breaking changes
  - Removing fields
  - Changing field types
  - Renaming fields
  - Changing field semantics
  
- **MINOR** (e.g., 1.1, 1.2): Backward-compatible additions
  - Adding new optional fields
  - Adding new enum values
  - Adding new nested objects

### Examples

```
"schema_version": "1.0"  → "schema_version": "1.1"  (add optional metadata)
"schema_version": "1.1"  → "schema_version": "2.0"  (remove deprecated field)
```

---

## Embedded schema versioning

Each snapshot contains:

```json
{
  "schema_version": "2.1",
  "entity": { ... }
}
```

---

## Backward compatibility rules

Readers must support N-1 schema versions

New writers emit only the latest schema

Incompatible changes require:
- MAJOR version bump
- Reader upgrade before writer rollout

---

## Migration approach

No in-place mutation of snapshots

Optional background rewrite:
- Read old snapshot
- Write new snapshot version
- Advance head pointer

History remains intact.
