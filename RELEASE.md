# Release Notes

This file documents the release history of entitybase-backend.

For the latest development changes, see [CHANGELOG.md](CHANGELOG.md).

---

## [v1.0.0-alpha1] - 2026-02-18

### Added

#### Entity Protection Endpoints
- **Lock/Unlock**: Full edit lock on entities
  - `POST /entities/{entity_id}/lock` - Lock entity
  - `DELETE /entities/{entity_id}/lock` - Remove lock
- **Archive/Unarchive**: Archive entities
  - `POST /entities/{entity_id}/archive` - Archive entity
  - `DELETE /entities/{entity_id}/archive` - Unarchive entity
- **Semi-protect/Unprotect**: Semi-protection (only autoconfirmed users can edit)
  - `POST /entities/{entity_id}/semi-protect` - Semi-protect entity
  - `DELETE /entities/{entity_id}/semi-protect` - Remove semi-protection
- **Mass-edit-protect/Unprotect**: Mass edit protection
  - `POST /entities/{entity_id}/mass-edit-protect` - Add mass edit protection
  - `DELETE /entities/{entity_id}/mass-edit-protect` - Remove mass edit protection

All protection endpoints are **idempotent** - returns success if entity is already in target state.

#### Request/Response Models
- `EntityStatusRequest` - Optional edit summary
- `EntityStatusResponse` - Returns entity_id, rev_id, status, and idempotent flag

### New Files
- `src/models/data/rest_api/v1/entitybase/request/entity/entity_status.py`
- `src/models/data/rest_api/v1/entitybase/response/entity/entity_status.py`
- `src/models/rest_api/entitybase/v1/services/status_service.py`
- `src/models/rest_api/entitybase/v1/handlers/entity/status.py`

### Modified Files
- `src/models/data/infrastructure/s3/enums.py` - Added new EditType values
- `src/models/rest_api/entitybase/v1/endpoints/entities.py` - Added 8 new endpoints

---

## [Unreleased] - YYYY-MM-DD

*(See CHANGELOG.md for current development)*
