# Schema Definitions

JSON Schema definitions for Wikibase backend.

## Versioning Structure

Schemas are organized by type and version using the following structure:

```
src/schemas/
├── entitybase/
│   ├── entity/           # Single entity response schemas
│   │   ├── 1.0.0/
│   │   │   └── schema.json
│   │   └── latest/
│   │       └── latest.json -> ../1.0.0/schema.json
│   ├── entities/         # Entities list response schemas
│   │   ├── 1.0.0/
│   │   │   └── schema.json
│   │   └── latest/
│   │       └── latest.json -> ../1.0.0/schema.json
│   ├── s3-revision/      # S3 revision data schemas
│   │   ├── 1.0.0/
│   │   │   └── schema.json
│   │   ├── 1.1.0/
│   │   │   └── schema.json
│   │   ├── 1.2.0/
│   │   │   └── schema.json
│   │   ├── 2.1.0/
│   │   │   └── schema.yaml
│   │   └── latest/
│   │       └── latest.yaml -> ../2.1.0/schema.yaml
│   └── s3-statement/     # S3 statement data schemas
│       ├── 1.0.0/
│       │   └── schema.json
│       └── latest/
│           └── latest.json -> ../1.0.0/schema.json
└── wikibase/
    └── entity/           # Wikibase REST API entity schemas
        ├── 1.0.0/
        │   └── schema.json
        └── latest/
            └── latest.json -> ../1.0.0/schema.json
```

## Rules

- Each schema type has its own subdirectory (e.g., `entitybase/entity/`)
- Versions use [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH)
- Each version has a `schema.json` file containing the JSON schema
- The `latest/` subdirectory contains `latest.json` which symlinks to the highest version's `schema.json`
- When adding a new version, update the `latest/latest.json` symlink to point to the new version
- Include a `README.md` in version directories if there are breaking changes or important notes

## Usage

To validate data against the latest schema:

```python
import json
import jsonschema

# Load the schema
with open('src/schemas/entitybase/entity/latest/latest.json', 'r') as f:
    schema = json.load(f)

# Validate data
jsonschema.validate(data, schema)
```

For a specific version:

```python
with open('src/schemas/entitybase/entity/1.0.0/schema.json', 'r') as f:
    schema = json.load(f)
```

## Schema Types

### Entity API Response Schema

JSON Schema for EntityBase JSON Entity v1 API responses from entity read endpoints.

Version: `1.0.0` (latest: `latest` symlink)

### Entity API Response Schema

JSON Schema for EntityBase JSON Entity v1 API responses from entity read endpoints.

Version: `1.0.0` (latest: `latest` symlink)

### Entities List Response Schema

JSON Schema for EntityBase entities list API responses from entities list endpoints.

Version: `1.0.0` (latest: `latest` symlink)

### S3 Revision Schema

Immutable entity revision snapshots stored in S3 with deduplication for terms, sitelinks, and statements. Sitelinks and terms metadata are stored as plain UTF-8 text files keyed by hash.

Versions: `1.0.0`, `1.1.0`, `1.2.0`, `2.1.0` (latest: `2.1.0`)

### S3 Statement Schema

Statement data stored in S3. References and qualifiers are deduplicated using rapidhash pointers.

Versions: `1.0.0`, `2.0.0`, `3.0.0` (latest: `3.0.0`)

#### Example Statement (v3.0.0)

```json
{
  "schema_version": "3.0.0",
  "content_hash": 1234567890123456789,
  "statement": {
    "mainsnak": {
      "snaktype": "value",
      "property": "P31",
      "datatype": "wikibase-item",
      "datavalue": {
        "value": {
          "entity-type": "item",
          "numeric-id": 5,
          "id": "Q5"
        },
        "type": "wikibase-entityid"
      }
    },
    "type": "statement",
    "rank": "normal",
    "qualifiers": 1122334455667788990,
    "references": [
      9876543210987654321,
      8765432109876543210
    ]
  },
  "created_at": "2026-01-18T12:00:00Z"
}
```

In v3.0.0, `qualifiers` is a rapidhash integer pointing to deduplicated qualifiers JSON, and `references` contains rapidhash integers pointing to deduplicated reference JSON in the `wikibase-references` S3 bucket.

### Wikibase Entity Schema

JSON Schema for Wikibase REST API entity objects.

Version: `1.0.0` (latest: `latest` symlink)

### Wikibase Entity Schema

JSON Schema for Wikibase REST API entity objects.

Version: `1.0.0` (latest: `latest` symlink)

See `wikibase/entity/` directory.
