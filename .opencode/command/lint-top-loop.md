---
description: Run linters and fix issues in a loop until clean
agent: general
---
Run ./run-linters.sh and capture the output.
If there are any linting errors, fix them starting from the top of the list, prioritizing the first error.
Repeat running the linters and fixing until there are no more errors or issues remain that cannot be fixed automatically.
