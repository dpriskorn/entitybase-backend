---
description: Run coverage and report 80% coverage analysis
agent: plan
---
Run coverage report with branch analysis:
```
poetry run pytest --cov=src --cov-branch --cov-report=term-missing --cov-fail-under=80
```

Report:
1. Total coverage percentage (must be >= 80%)
2. All files with coverage below 80%
3. Branch coverage gaps - any if/else, try/except, or ternary branches not covered
4. Files with missing happy path coverage (public methods without any test)

Exclude from coverage requirements:
- src/models/data/rest_api/v1/entitybase/request (auto-generated)
- src/models/data/rest_api/v1/entitybase/response (auto-generated)
- */__init__.py
