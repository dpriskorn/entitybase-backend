# S3 Storage Architecture

S3 (rustfs/MinIO) is used exclusively for **dump file uploads**. All other data — revisions, statements, terms, sitelinks, and entity snapshots — lives in MariaDB.

## Bucket

| Bucket | Purpose |
|--------|---------|
| `wikibase-dumps` | Periodic full dumps of entity data |

## Dump Types

| Format | Workers | Content-Type | Description |
|--------|---------|--------------|-------------|
| JSON | `json-dump-worker` | `application/json` | Full entity export in Wikibase JSON format |
| TTL/RDF | `ttl-dump-worker` | `text/turtle` | Full entity export in Turtle RDF format |

Dumps may be gzip-compressed (`application/gzip`) depending on worker configuration.

## Object Path Convention

```
weekly/{date}/{filename}
```

Examples:
```
weekly/2026-08-24/full.json.gz
weekly/2026-08-24/full.ttl.gz
```

The `date` component follows ISO 8601 format (`YYYY-MM-DD`) and corresponds to the dump generation date.

## Object Metadata

Each S3 object stores the following metadata:

| Key | Description |
|-----|-------------|
| `x-amz-meta-sha256` | SHA-256 checksum of the uncompressed dump content |

This checksum allows downstream consumers to verify dump integrity independent of the transport layer.

## Upload Flow

1. A dump worker (`json-dump-worker` or `ttl-dump-worker`) reads entity data from MariaDB.
2. The worker streams the dump file to the `wikibase-dumps` bucket using boto3.
3. The SHA-256 checksum of the uncompressed content is attached as S3 object metadata.
4. The S3 key follows the `weekly/{date}/{filename}` convention.

## Design Rationale

Keeping S3 reserved for dump uploads keeps the hot path (reads and writes for revisions, statements, terms) entirely within MariaDB, avoiding S3 latency for entity operations. Dumps are inherently bulk, read-heavy, and consumed by external tooling — a natural fit for object storage.
