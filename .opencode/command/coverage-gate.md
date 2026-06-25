---
description: CI coverage gate - fail build if coverage < 80%
agent: plan
---
## Purpose
This agent runs as a CI gate to ensure coverage never drops below 80%.

## Execution
Run pytest with coverage and fail-under enforcement:
```bash
poetry run pytest --cov=src --cov-branch --cov-fail-under=80 --cov-report=term-missing
```

## Success Criteria
- Exit code 0 if coverage >= 80%
- Exit code 1 if coverage < 80%

## What This Checks
1. **Line coverage** >= 80% - every line in src/ is executed by tests
2. **Branch coverage** >= 80% - all decision points (if/else, try/except) have both branches tested

## Excluded from Coverage
- src/models/data/rest_api/v1/entitybase/request (auto-generated)
- src/models/data/rest_api/v1/entitybase/response (auto-generated)
- */__init__.py

## If Coverage Fails
1. Run `coverage.md` agent to get detailed report
2. Run `increase-unit-test-coverage.md` agent to add missing tests
3. Do NOT lower the threshold - always add tests to reach 80%
