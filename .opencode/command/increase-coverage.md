---
description: Increase coverage by suggesting new unit, integration and e2e tests
agent: plan
---
Read coverage.txt.
Avoid creating tests for everything in these directories:
src/models/data


Analyze and suggest new unit tests. 
All unit tests should mock only Client and ConnectionManager models.
Ask user before mocking anything else.
New tests has to be placed in the corresponding location in the tests/ directory.
The user wants the directory hierarchy of src/ and tests/ to be similar.