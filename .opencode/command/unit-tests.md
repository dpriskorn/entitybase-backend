---
description: Run unit tests and investigate test failures and suggest actions
agent: general
---
Run unit tests with ./run-unit-tests.sh
Analyze the errors and tell the user how many failed in number and % and suggest actions. 
If any edits were made, run ./run-linters.sh and analyze result and propose actions.
When done suggest commit message.
When approved, commit.