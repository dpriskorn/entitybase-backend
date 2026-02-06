---
description: Ensure endpoint test coverage
agent: plan
---
Read read src/models/rest_api/ENDPOINTS.md and make sure we have integration and e2e tests for all of them
No mocking in integration and E2E tests.
E2E tests should only test using public endpoints.
New tests has to be placed in the corresponding location in the tests/ directory.
The user wants the directory hierarchy of src/ and tests/ to be similar.