#!/bin/bash
set -e

echo "Running JSON lint: Detecting json.dumps usage and recommending model_dump(mode='json')"

# Find all occurrences of json.dumps in Python files
violations=$(grep -r "json\.dumps" src/ --include="*.py" | wc -l)

if [ "$violations" -gt 0 ]; then
    echo "Found $violations occurrence(s) of json.dumps."
    echo "Consider replacing json.dumps(model.model_dump()) with json.dumps(model.model_dump(mode='json')) for better JSON serialization."
    grep -r "json\.dumps" src/ --include="*.py"
    exit 1
else
    echo "No json.dumps violations found."
fi