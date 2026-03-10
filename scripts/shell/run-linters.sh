#!/bin/bash
cd "$(dirname "$0")/../.."
set -e

export PATH="$PWD/.venv/bin:$PATH"

# == custom internal linters ==
poetry run python scripts/linters/check_async_calls.py src/
./scripts/shell/run-int-lint.sh
poetry run python scripts/linters/value_error_linter.py
./scripts/shell/run-assert-linter.sh
./scripts/shell/run-response-model-lint.sh
./scripts/shell/run-logger-lint.sh
./scripts/shell/run-long-files-lint.sh
./scripts/shell/run-dict-lint.sh
./scripts/shell/run-pydantic-field-lint.sh
./scripts/shell/run-any-lint.sh
./scripts/shell/run-tuple-lint.sh
./scripts/shell/run-key-length-lint.sh
./scripts/shell/run-init-lint.sh
./scripts/shell/run-backslash-lint.sh
./scripts/shell/run-json-lint.sh
./scripts/shell/run-status-code-lint.sh

# == external linters ==
./scripts/shell/run-ruff.sh
./scripts/shell/run-radon.sh
./scripts/shell/run-mypy.sh
./scripts/shell/run-vulture.sh
