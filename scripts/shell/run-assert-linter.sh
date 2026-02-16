#!/bin/bash
cd "$(dirname "$0")/../.."

# Run assert statement linter on src/
python scripts/linters/check_assert_statements.py src/
