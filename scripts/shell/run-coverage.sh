#!/bin/bash
cd "$(dirname "$0")/../.."
set -e

THRESHOLD=80
ENV_FILE="${1:-minimal}"

source "test-${ENV_FILE}.env"

echo "Cleaning up..."

rm coverage_below_threshold.txt || true
rm coverage.txt || true
rm coverage.xml || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

echo "Running all tests with coverage (env=${ENV_FILE})..."
poetry run pytest \
  -n "auto" \
  --cov=src \
  --cov-report=term-missing \
  --cov-report=xml:coverage.xml > coverage.txt

if [[ -f coverage.xml ]]; then
  echo "Coverage reports generated: coverage.txt, htmlcov/, coverage.xml"
  poetry run python scripts/generate_coverage_report.py $THRESHOLD
else
  echo "coverage.xml not found. Make sure pytest ran successfully."
  exit 1
fi
