# Wikibase Entity Schema

This schema defines the structure for Wikibase entity objects, including items, properties, and lexemes. It includes labels, descriptions, aliases, claims (statements), and sitelinks.

## Mock Example
```json
{
  "id": "Q123",
  "type": "item",
  "labels": {
    "en": {
      "language": "en",
      "value": "Test Item"
    }
  },
  "descriptions": {
    "en": {
      "language": "en",
      "value": "A test item for demonstration"
    }
  },
  "aliases": {
    "en": [
      {
        "language": "en",
        "value": "Test"
      }
    ]
  },
  "claims": {
    "P31": [
      {
        "mainsnak": {
          "snaktype": "value",
          "property": "P31",
          "datavalue": {
            "value": {
              "entity-type": "item",
              "id": "Q5"
            },
            "type": "wikibase-entityid"
          },
          "datatype": "wikibase-item"
        },
        "type": "statement",
        "rank": "normal"
      }
    ]
  },
  "sitelinks": {
    "enwiki": {
      "site": "enwiki",
      "title": "Test Item"
    }
  }
}
```