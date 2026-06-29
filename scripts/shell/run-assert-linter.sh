#!/bin/bash
cd "$(dirname "$0")/../.."

# Run assert statement linter on src/
poetry run python scripts/linters/check_assert_statements.py src/
