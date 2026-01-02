# Wikidata Dump Filtering & Import Experiment

This repository documents an experiment to **filter Wikidata JSON dumps locally** and **import a reduced subset into an API-backed storage system** (e.g. S3-compatible object storage + ingestion API).

The primary goal is to:
- Minimize storage and processing cost
- Validate ingestion and serialization logic
- Incrementally scale from small, well-defined subsets

---

## Scope

Initial scope is intentionally limited to:

- **Entity type:** Wikidata properties (`P*`)
- **Source:** Official Wikidata JSON dumps
- **Filtering:** Streaming, pre-import filtering
- **Ingestion:** Send filtered JSON to a custom API endpoint

Properties are chosen because:
- There are only ~15k entities
- They define datatypes and semantics required for item processing
- They are sufficient to bootstrap RDF or indexing pipelines

---

## Data Source

Wikidata JSON dumps:

- `latest-all.json.bz2` (recommended)
- Downloaded from Wikimedia dumps infrastructure

The dump contains **one JSON entity per line**, wrapped in a top-level JSON array.

---

## Tooling

### wikidata-dump-filter

Filtering is performed using Maxlath’s `wikidata-dump-filter`:

- Streams compressed dumps
- Does not require full decompression
- Filters entity-by-entity

Repository:
- https://github.com/maxlath/wikidata-dump-filter

---

## Step 1: Download Dump

```bash
wget https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2

## Step 2: Extract Properties Only

```bash
wikidata-dump-filter \
  --input latest-all.json.bz2 \
  --output properties.json \
  --entity-type property
```

This produces a valid Wikidata JSON dump containing only P* entities.

## Step 3: (Optional) Recompress

Recommended before upload or archival:

zstd -19 properties.json
# or
bzip2 properties.json


Expected size:

~20–60 MB compressed
~200–400 MB uncompressed

## Step 4: Send to API Endpoint

Assumes an API endpoint capable of receiving Wikidata JSON entities.

Example: streaming upload
```bash
cat properties.json \
| curl -X POST \
    -H "Content-Type: application/json" \
    --data-binary @- \
    https://example.org/api/import/wikidata
```

Example: line-by-line ingestion
```bash
jq -c '.[]' properties.json | while read -r entity; do
  curl -X POST \
    -H "Content-Type: application/json" \
    -d "$entity" \
    https://example.org/api/import/wikidata/entity
done
```
