# Immutable Revisions

Every edit creates an immutable snapshot that can never be overwritten.

## Overview

Entitybase follows an **append-only** model where every edit creates a new revision stored in S3. Once written, a revision can never be modified or deleted — it's permanent.

## How It Works

1. When you create or update an entity, a new revision is created
2. The revision is stored as an immutable object in S3
3. A "head pointer" in Vitess points to the latest revision
4. All previous revisions remain accessible

## Benefits

- **Perfect audit trail** — Who changed what, when
- **Easy rollbacks** — Just point to an old revision
- **No data loss** — Old versions are never deleted
- **Event sourcing** — Replay events to rebuild state
- **Conflict resolution** — Compare revisions without locking

## Revision Access

| Endpoint | Description |
|----------|-------------|
| GET `/entities/{type}/{id}/revisions` | List all revisions |
| GET `/entities/{type}/{id}/revisions/{rev_id}` | Get specific revision |
| GET `/entities/{type}/{id}/revisions/latest` | Get latest revision |

## Comparison

```
Traditional database:     Entitybase:
┌─────────────┐         Rev 1: Q1 ──▶ S3
│    Q1       │         Rev 2: Q1 ──▶ S3  
│  (current)  │         Rev 3: Q1 ──▶ S3
└─────────────┘         (all preserved!)
  (overwrites!)
```

See also: [Architecture](../ARCHITECTURE/ARCHITECTURE.md)
