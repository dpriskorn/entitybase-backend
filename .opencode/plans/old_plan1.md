# Plan: Replace Generic Entity Endpoints with Item-Specific Ones

## Summary
Remove the generic `POST /v0/entities` and `PUT /v0/entities/{id}` endpoints and replace them with item-specific `POST /v0/entities/items` and `PUT /v0/entities/items/{id}` (focusing on items for now). This uses dedicated handlers like `ItemCreateHandler` and `EntityUpdateHandler` for type-specific handling.

## Current Generic Endpoints
- **POST /v0/entities**: Stub TODO for generic creation.
- **PUT /v0/entities/{id}**: Generic update (uses `EntityUpdateHandler`).

## Proposed Item-Specific Endpoints
- **Remove**:
  - `POST /v0/entities` (generic creation stub).
  - `PUT /v0/entities/{id}` (generic update).
- **Add**:
  - `POST /v0/entities/items` → Uses `ItemCreateHandler.create_item` (already implemented).
  - `PUT /v0/entities/items/{id}` → Uses `EntityUpdateHandler.update_entity` with item validation.

## Implementation Steps
1. **Remove Generic Routes** (`src/models/rest_api/main.py`):
   - Delete `@v0_router.post("/entities")` (the TODO stub).
   - Delete `@v0_router.put("/entities/{entity_id}")`.

2. **Add Item-Specific Routes** (`src/models/rest_api/main.py`):
   - Add `@v0_router.post("/entities/items")` → Call `item_create_handler.create_item`.
   - Add `@v0_router.put("/entities/items/{entity_id}")` → Call `entity_update_handler.update_entity` (ensure it validates item type).

3. **Handler Adjustments** (`src/models/rest_api/handlers/entity/update.py`):
   - In `update_entity`, add type check: Ensure `entity_id` starts with "Q" or validate via enumeration.
   - Keep existing transaction logic.

4. **Cleanup**:
   - Remove unused imports/handlers for generic creation.
   - Update docs/diagrams to reflect item-specific routes.

## Tradeoffs and Considerations
- **Pros**: Simpler, type-safe for items; avoids generic TODO.
- **Cons**: Not extensible to other types yet; more routes to manage.
- **Effort**: Low (route changes); leverages existing handlers.

## Testing and Validation
- **Unit Tests**: Update route tests to use item-specific paths.
- **Integration**: Verify item creation/update works via new endpoints.
- **Run Linters**: Ensure no regressions.

## Clarifying Questions
- Should the update endpoint validate that `{entity_id}` is an item (e.g., starts with "Q")?
- Keep other generic routes (e.g., GET /v0/entities/{id}) or make them item-specific too?
- Plan to add other types later, or focus on items?