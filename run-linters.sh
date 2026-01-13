#!/bin/bash
set -e

# == custom internal linters ==
#./scripts/linters/custom_docstring_linter.py
#./scripts/linters/basemodel_linter.py
./run-str-lint.sh
./run-int-lint.sh
./scripts/linters/value_error_linter.py
./run-response-model-lint.sh
./run-logger-lint.sh
./run-long-files-lint.sh
./run-dict-lint.sh
./run-pydantic-field-lint.sh
./run-any-lint.sh
./run-cast-lint.sh
./run-tuple-lint.sh
./run-data-lint.sh

# == external linters ==
./run-ruff.sh
./run-mypy.sh
./run-vulture.sh
./run-radon.py