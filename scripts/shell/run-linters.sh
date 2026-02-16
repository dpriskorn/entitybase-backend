#!/bin/bash
cd "$(dirname "$0")/../.."
set -e

# == custom internal linters ==
#./scripts/linters/custom_docstring_linter.py
#./scripts/linters/basemodel_linter.py
#./scripts/shell/run-data-lint.sh
#./scripts/shell/run-str-lint.sh
./scripts/shell/run-int-lint.sh
./scripts/linters/value_error_linter.py
./scripts/shell/run-assert-linter.sh
./scripts/shell/run-response-model-lint.sh
./scripts/shell/run-logger-lint.sh
./scripts/shell/run-long-files-lint.sh
./scripts/shell/run-dict-lint.sh
./scripts/shell/run-pydantic-field-lint.sh
./scripts/shell/run-any-lint.sh
#./scripts/shell/run-cast-lint.sh
./scripts/shell/run-tuple-lint.sh
#./scripts/shell/run-as-lint.sh
./scripts/shell/run-key-length-lint.sh
./scripts/shell/run-init-lint.sh
#./scripts/shell/run-description-lint.sh
./scripts/shell/run-backslash-lint.sh
./scripts/shell/run-json-lint.sh
./scripts/shell/run-status-code-lint.sh

# == external linters ==
./scripts/shell/run-ruff.sh
./scripts/shell/run-radon.sh
./scripts/shell/run-mypy.sh
./scripts/shell/run-vulture.sh
