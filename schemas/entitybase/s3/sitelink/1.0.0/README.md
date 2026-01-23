# S3 Sitelink Data Schema v1.0.0

This schema defines the structure for sitelink data stored in Wikibase S3 revisions.

## Purpose

Sitelinks in Wikibase include a title (linked to a Wikipedia page) and optional badges (e.g., "featured article"). Previously, only title hashes were stored, losing badges. This schema enables storing both title hash and badges in revision data for full fidelity.

## Structure

- `title_hash`: Integer hash of the sitelink title (used to deduplicate and retrieve the title from S3).
- `badges`: Array of strings representing badges (defaults to empty array).

## Example

```json
{
  "title_hash": 123456789,
  "badges": ["featured"]
}
```

## Validation

This schema ensures:
- `title_hash` is required and an integer.
- `badges` is an optional array of strings.

## Migration Notes

Revisions using this schema are incompatible with older parsers expecting integer-only sitelinks. Use schema versioning for backwards compatibility.