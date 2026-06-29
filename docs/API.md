# Entitybase Backend API Documentation
**Version**: v1.2026.3.2  
**Base URL**: See `/docs` for interactive API explorer

---

## Quick Start: Creating Entities

### Creating an Item

**Note:** Currently, item creation only supports empty items. Use the endpoint below to create an item, then add labels/descriptions using the update endpoints.

```bash
# Create an empty item
curl -X POST https://api.example.com/v1/entities/items \
  -H "X-User-ID: 1" \
  -H "X-Edit-Summary: Creating new item"
```

### Creating a Lexeme (with full data)

Lexeme creation supports full entity data in the request body:

```json
{
  "type": "lexeme",
  "language": "Q1860",
  "lexicalCategory": "Q1084",
  "lemmas": {"en": {"language": "en", "value": "test"}},
  "labels": {"en": {"language": "en", "value": "test lexeme"}},
  "forms": [
    {
      "representations": {"en": {"language": "en", "value": "tests"}},
      "grammaticalFeatures": ["Q110786"]
    }
  ],
  "senses": [
    {
      "glosses": {"en": {"language": "en", "value": "a test"}}
    }
  ]
}
```

### Adding Labels and Descriptions to Existing Entities

After creating an entity, add labels using:

```bash
# Add a label
curl -X PUT https://api.example.com/v1/entities/Q123/labels/en \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -H "X-Edit-Summary: Adding label" \
  -d '{"language": "en", "value": "My Item"}'
```

### MonolingualText Format

Labels, descriptions, aliases, and other term data use the MonolingualText format:

```json
{
  "language": "en",
  "value": "The text content"
}
```

---

## Authentication
All endpoints requiring modifications (POST, PUT, PATCH, DELETE) require headers:
| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `X-User-ID` | integer | Yes | User ID making the edit |
| `X-Edit-Summary` | string | Yes | Edit summary (1-200 chars) |
| `X-Base-Revision-ID` | integer | No | For optimistic locking |

---

## Table of Contents

| Category | Description | Link |
|----------|-------------|------|
| **Items** | Create, read, update, delete items (Q IDs) | [ITEMS.md](api/ITEMS.md) |
| **Properties** | Property entities (P IDs) | [PROPERTIES.md](api/PROPERTIES.md) |
| **Lexemes** | Lexeme entities with forms, senses | [LEXEMES.md](api/LEXEMES.md) |
| **Entities** | General entity operations | [ENTITIES.md](api/ENTITIES.md) |
| **Statements** | Statement CRUD, deduplication | [STATEMENTS.md](api/STATEMENTS.md) |
| **Statistics** | Wiki statistics, deduplication stats | [STATISTICS.md](api/STATISTICS.md) |
| **Watchlist** | User watchlists | [WATCHLIST.md](api/WATCHLIST.md) |
| **Import** | Wikidata JSON import | [IMPORT.md](api/IMPORT.md) |
| **Redirects** | Entity redirects | [REDIRECTS.md](api/REDIRECTS.md) |
| **List** | Entity listing and search | [LIST.md](api/LIST.md) |
| **Health** | Health check endpoints | [HEALTH.md](api/HEALTH.md) |
| **Version** | API version info | [VERSION.md](api/VERSION.md) |
| **Settings** | User settings | [SETTINGS.md](api/SETTINGS.md) |
| **Interactions** | Thanks, endorsements | [INTERACTIONS.md](api/INTERACTIONS.md) |
| **Users** | User management | [USERS.md](api/USERS.md) |
| **Data Models** | Request/Response schemas | [DATA_MODELS.md](api/DATA_MODELS.md) |

---

## Base URL

```
/v1/entitybase
```

For local development: `http://localhost:8000/v1/entitybase`

---

## Interactive API Explorer

For full interactive documentation, visit: `http://localhost:8000/docs`

---

## Related Documentation

- [Quick Reference](../QUICKREF.md) - One-page command reference
- [Getting Started](../GETTING_STARTED.md) - Quick start guide
- [Glossary](../GLOSSARY.md) - Domain terms explained