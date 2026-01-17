#!/bin/bash
set -e

echo "Checking for descriptions in API response models..."
python scripts/linters/description_linter.py src/models/rest_api/entitybase/response
echo "Description check passed!"