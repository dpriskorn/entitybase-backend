# Import API

> API endpoints for importing entities from Wikidata JSON format

---

## POST /v1/import
**Import a single entity (item, property, or lexeme)**

Import a single entity of any type.

This unified endpoint accepts items, properties, and lexemes.
The entity type is determined by the 'type' field in the request.

**Supported entity types:**
- item: Q-prefixed entities (e.g., Q42)
- property: P-prefixed entities (e.g., P31)
- lexeme: L-prefixed entities (e.g., L123)

**Parameters:**
- id: Entity ID (required for import, auto-assignment not supported)
- type: Entity type (item, property, lexeme)
- labels: Language-specific labels
- descriptions: Language-specific descriptions
- claims: Statements/claims
- sitelinks: Site links (items only)
- forms: Forms (lexemes only)
- senses: Senses (lexemes only)
- lemmas: Lemmas (lexemes only)
- aliases: Aliases

**Returns:** EntityResponse with created entity data

**Errors:**
- 409: Entity already exists
- 400: Validation error

| Aspect | Details |
|--------|---------|
| Operation ID | `import_entity_v1_import_post` |
| Method | `POST` |
| Path | `/v1/import` |
| Request Body | `[EntityCreateRequest](#entitycreaterequest)` |
| Response | Description |
|----------|-------------|
| 200 | Successful Response |
| 422 | Validation Error |

---

## Related Links

- [← Back to API](../API.md)
- [Entities API](./ENTITIES.md)