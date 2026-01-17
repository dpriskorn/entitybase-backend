#!/bin/bash
set -e

echo "Checking for long field names in API response models..."
python scripts/linters/key_length_linter.py src/models/rest_api/entitybase/response
echo "Field name length check passed!"