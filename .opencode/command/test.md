---
description: Investigate test failures and suggest actions
agent: general
---
Investigate docker integration-tests e.g. with ./get-docker-logs.sh
Analyze the errors and suggest actions. 
Never run any docker compose up commands, tell the user to test when ready instead.
When done with approved action, /run-linter.sh and analyze result and propose actions.
When done suggest commit message.
When approved, commit.