# Test Data Directory

This directory contains test fixtures for integration and unit testing.

## Directory Structure

```
test_data/
├── json/
│   ├── entities/          # Wikibase JSON (external/Wikidata API format)
│   ├── revisions/         # S3 revision schema (internal format)
│   ├── errors/            # Error response fixtures
│   └── change/           # RDF change events
├── rdf/                  # RDF test data (Turtle, NTriples)
├── entity_redirects/     # Entity redirect fixtures
├── README.md             # General overview
└── AGENTS.md            # This file
```

## Golden Wikibase JSON (entities/)

Files in `json/entities/` represent the **Wikidata API JSON response format**.

### Key Characteristics

- **Format**: External Wikidata API format
- **Case**: Uses camelCase (Wikidata standard)
- **Contains**: Complete entity data as returned by Wikidata API

### Common camelCase Fields

| Field | Description |
|-------|-------------|
| `lexicalCategory` | Lexeme lexical category (QID) |
| `grammaticalFeatures` | Form grammatical features |
| `lastrevid` | Last revision ID |
| `entity-type` | Entity type (within datavalue) |
| `numeric-id` | Numeric entity ID |
| `mainsnak` | Main snak of a statement |
| `snaktype` | Type of snak (value, novalue, somevalue) |
| `datavalue` | Value of a snak |
| `datatype` | Data type of property |

### Example Structure

```json
{
  "entities": {
    "L42": {
      "pageid": 54387043,
      "title": "Lexeme:L42",
      "type": "lexeme",
      "id": "L42",
      "lexicalCategory": "Q1084",
      "language": "Q1860",
      "claims": {
        "P31": [
          {
            "mainsnak": {
              "snaktype": "value",
              "property": "P31",
              "datavalue": {
                "value": {"entity-type": "item", "numeric-id": 5, "id": "Q5"},
                "type": "wikibase-entityid"
              },
              "datatype": "wikibase-item"
            }
          }
        ]
      }
    }
  }
}
```

## Internal Data Formats

Files in other directories use snake_case:

- `json/revisions/` - S3 revision storage format
- `json/errors/` - Error responses

## API Request Format Support

The API supports both **Wikidata JSON format** (camelCase) and **snake_case** for requests.

### Test Files (tests/)

Test files can use either format:

```python
# Option 1: camelCase (Wikidata format - recommended for lexeme tests)
lexeme_data = {
    "type": "lexeme",
    "language": "Q1860",
    "lexicalCategory": "Q1084",  # camelCase
    "lemmas": {"en": {"language": "en", "value": "test"}},
    "forms": [
        {
            "representations": {"en": {"language": "en", "value": "tests"}},
            "grammaticalFeatures": ["Q110786"],  # camelCase
        },
    ],
}

# Option 2: snake_case
lexeme_data = {
    "type": "lexeme",
    "language": "Q1860",
    "lexical_category": "Q1084",  # snake_case
    "lemmas": {"en": {"language": "en", "value": "test"}},
    "forms": [
        {
            "representations": {"en": {"language": "en", "value": "tests"}},
            "grammatical_features": ["Q110786"],  # snake_case
        },
    ],
}
```

### Implementation Details

The request models use Pydantic's `AliasChoices` to accept both formats:

```python
from pydantic import AliasChoices, Field

class EntityCreateRequest(BaseModel):
    lexical_category: str = Field(
        default="",
        description="Lexeme lexical category (QID)",
        validation_alias=AliasChoices("lexical_category", "lexicalCategory"),
    )
```

See `src/models/data/rest_api/v1/entitybase/request/entity/entity_create_request.py` for the implementation.

## Adding New Test Data

When adding new entity test data:

1. Use Wikidata API JSON format (camelCase) for `entities/`
2. Include complete entity with all relevant fields
3. Name files after entity ID (e.g., `L42.json`, `Q42.json`)
