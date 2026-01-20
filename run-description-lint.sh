#!/bin/bash
set -e

echo "Checking for descriptions in API response models..."
python scripts/linters/description_linter.py src/models/rest_api/entitybase/v1/response
echo "Description check passed!"