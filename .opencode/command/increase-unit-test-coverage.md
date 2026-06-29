---
description: Increase coverage to 80% with happy path and logic focus
agent: plan
---
## Coverage Target
Increase test coverage to 80% minimum (line AND branch coverage).

## Priority Order
1. **Happy paths** - Test the default/expected behavior of public methods first
2. **Branch logic** - Cover all if/else, try/except, and ternary branches
3. **Error paths** - Only after happy paths are covered

## What to Test
- All public methods have at least one passing test
- All conditional branches (if/else, match/case) have tests for each branch
- All try/except blocks have tests for both success and exception paths
- Repository methods return expected types and values

## What NOT to Test
- src/models/data/rest_api/v1/entitybase/request (auto-generated)
- src/models/data/rest_api/v1/entitybase/response (auto-generated)
- */__init__.py files

## Rules
1. Mock only Client and ConnectionManager models - never mock mysql or s3 directly
2. Ask user before mocking anything other than Client/ConnectionManager
3. Unit tests go in tests/unit/models/ mirroring src/models/ structure
4. Use pytest-mock for mocking external dependencies
5. Keep tests focused: one assertion per test function when possible
6. Happy path first, then edge cases

## Test Organization
Tests directory must mirror src/models/ structure:
```
tests/unit/models/
├── config/
├── data/
├── infrastructure/
├── internal_representation/
├── json_parser/
├── rdf_builder/
├── rest_api/
├── services/
├── validation/
└── workers/
```

## Verification
Run coverage to verify 80% target:
```
poetry run pytest --cov=src --cov-branch --cov-fail-under=80
```
