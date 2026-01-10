# Wikibase Entity Schema

JSON Schema for Wikibase REST API entity objects.

## Schema Inference

This schema was inferred from the Wikibase REST API response format, using `test_data/json/entities/Q42.json` as the reference entity.

The schema validates standard Wikibase entity structures including:
- Entity metadata (id, type)
- Multilingual labels, descriptions, and aliases
- Claims (statements) with mainsnak, qualifiers, and references
- Sitelinks

## Version History

### 1.0.0 (2026-01-10)
- Initial schema creation
- Supports items, properties, and lexemes
- Comprehensive validation for all Wikibase datatypes and structures
- Based on Wikidata Q42 entity structure
- Verified working for Q1