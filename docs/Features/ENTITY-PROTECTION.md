# Entity Protection

Protect entities from unwanted edits with various protection levels.

## Overview

Entitybase supports multiple protection levels to control who can edit entities. This is essential for community governance and preventing vandalism.

## Protection Types

### Lock 🔒
Prevents all edits to an entity. Only administrators can unlock.

**Endpoint:** `POST/DELETE /entities/{id}/lock`

### Semi-Protect ⚠️
Allows only established users to edit. Configurable based on user rights.

**Endpoint:** `POST/DELETE /entities/{id}/semi-protect`

### Archive 📁
Marks an entity as archived — hidden from normal views but restorable.

**Endpoint:** `POST/DELETE /entities/{id}/archive`

### Mass-Edit Protect 🚫
Prevents bulk edits through the API while allowing single edits. Useful for preventing automated vandalism.

**Endpoint:** `POST/DELETE /entities/{id}/mass-edit-protect`

## Properties

- **Idempotent** — All endpoints return success if entity is already in target state
- **Reversible** — All protections can be undone
- **Audit trail** — Protection changes are logged in revision history

## Use Cases

- Protect famous/popular items from vandalism
- Semi-protect items that need some community editing
- Archive deprecated or obsolete entities
- Prevent automated spam attacks
