#!/bin/bash
set -e

./scripts/custom_docstring_linter.py
./scripts/basemodel_linter.py
./run-ruff.sh
./run-mypy.sh
#./run-vulture.sh
./run-radon.py