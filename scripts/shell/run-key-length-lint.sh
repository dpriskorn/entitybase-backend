#!/bin/bash
cd "$(dirname "$0")/../.."
set -e

echo "Checking for long field names in API response models..."
python scripts/linters/check_response_model_key_length.py src/models/data/rest_api/v1/entitybase/response
echo "Field name length check passed!"