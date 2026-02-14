#!/bin/bash
set -e

# == custom internal linters ==
#./scripts/linters/custom_docstring_linter.py
#./scripts/linters/basemodel_linter.py
#./run-data-lint.sh
#./run-str-lint.sh
./run-int-lint.sh
./scripts/linters/value_error_linter.py
./run-assert-linter.sh
./run-response-model-lint.sh
./run-logger-lint.sh
./run-long-files-lint.sh
./run-dict-lint.sh
./run-pydantic-field-lint.sh
./run-any-lint.sh
#./run-cast-lint.sh
./run-tuple-lint.sh
#./run-as-lint.sh
./run-key-length-lint.sh
./run-init-lint.sh
#./run-description-lint.sh
./run-backslash-lint.sh
./run-json-lint.sh
./run-status-code-lint.sh

# == external linters ==
./run-ruff.sh
./run-radon.sh
./run-mypy.sh
./run-vulture.sh
