#!/bin/bash
set -e

echo "Checking for docstrings in API response models..."
python scripts/linters/docstring_linter.py src/models/rest_api/entitybase/response
echo "Docstring check passed!"