# Fixes Applied

## 1. Fixed Import Error in test_id_generator.py
- **File**: `tests/unit/models/workers/test_id_generator.py`
- **Change**: Updated import from `models.workers.id_generation.id_generation_worker.IdResponse` to `models.data.rest_api.v1.entitybase.response.id_response.IdResponse`

## 2. Renamed Duplicate test_main.py Files
Renamed 3 files to avoid pytest import conflicts:
- `tests/unit/models/workers/notification_cleanup/test_main.py` → `test_main_notification_cleanup.py`
- `tests/unit/models/workers/watchlist_consumer/test_main.py` → `test_main_watchlist_consumer.py`
- `tests/unit/models/rest_api/test_main.py` → `test_main_rest_api.py`

## 3. Deleted Placeholder Test Files
Removed 2 files that contained only placeholder tests:
- `tests/unit/models/json_parser/test_qualifier_parser.py` (placeholder)
- `tests/unit/models/json_parser/test_value_parser.py` (placeholder)
- These tests exist properly in `parsers/` subdirectory

## 4. Renamed Module-Level Parser Tests
Renamed 3 files to avoid conflicts with `parsers/` subdirectory:
- `tests/unit/models/json_parser/test_reference_parser.py` → `test_reference_parser_module.py`
- `tests/unit/models/json_parser/test_entity_parser.py` → `test_entity_parser_module.py`
- `tests/unit/models/json_parser/test_statement_parser.py` → `test_statement_parser_module.py`

All changes saved locally. Test collection errors should now be resolved.
