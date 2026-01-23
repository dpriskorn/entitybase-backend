---
description: Increase coverage by suggesting new unit tests
agent: general
---
Read coverage.txt.
Avoid creating tests for everything in these directories:
src/models/data


Analyze and suggest new unit tests. 
All unit tests should mock only Client and ConnectionManager models.
Ask user before mocking anything else.
New tests has to be placed in the corresponding location in the tests/ directory.
The user wants the src/ and tests/ to correspond.
When done with approved action, ./run-linters.sh and analyze result and propose a list of tasks. 
and wait for the user to approve the task list.