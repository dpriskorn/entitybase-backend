#!/bin/bash

# Run integration tests in parallel
# Uses pytest-xdist for parallel execution
# -n auto automatically detects available CPU cores

set -e

echo "Running integration tests in parallel..."
pytest -m integration -n auto --tb=short

echo "Integration tests completed."