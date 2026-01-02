# Entity Deletion

## Soft delete (default)

Deletion is a new immutable revision:

{
  "is_deleted": true,
  "is_redirect": false
}

Entity remains addressable

History preserved

Head points to tombstone

---

## Hard delete (exceptional)

Head pointer removed

Entity hidden from normal reads

Snapshots retained for retention period

Physical deletion via lifecycle rules only

Hard deletes are rare.
