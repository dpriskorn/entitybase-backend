# Conceptual Model

## Entity

An entity is a logical identifier only.

- `entity_id` (e.g. Q123)
- `entity_type` (item, property, lexeme, …)

Entities have no intrinsic state outside revisions.

An entity is a stable identifier only.

- `entity_id` (e.g. Q123)
- `entity_type` (item, property, lexeme, …)

Entities have no intrinsic state outside revisions.

---

## Revision

A revision is a complete, immutable snapshot of an entity.

- `entity_id`
- `revision_id` (monotonic per entity or content-hash based)
- `created_at`
- `revision_data` (MariaDB entity_revisions row)

Example:

entity_revisions row: entity_id=Q123, revision_id=42, entity_json={...}

Revision properties:
- Full canonical JSON
- Deterministic ordering
- Schema version embedded
- Written once, never modified


A revision is a complete snapshot of an entity.

- `entity_id`
- `revision_id` (monotonic per entity)
- `created_at`
- `revision_data` (MariaDB)
- `schema_version`
- `content_hash`


---
