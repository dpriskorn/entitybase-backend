#!/bin/bash
set -e

#./scripts/linters/custom_docstring_linter.py
#./scripts/linters/basemodel_linter.py
./scripts/linters/dict_return_linter.py
./run-ruff.sh
./run-mypy.sh
./run-vulture.sh
./run-radon.py