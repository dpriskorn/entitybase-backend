#!/bin/bash
cd "$(dirname "$0")/../.."
# set -euo pipefail

THRESHOLD=30

source test.env

source .venv/bin/activate

echo "Cleaning up..."

# Cleanup first
rm coverage_below_threshold.txt
rm coverage.txt
rm coverage.xml
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

echo "Running all tests with coverage..."
# Test
pytest \
  -n "auto" \
  --cov=src \
  --cov-report=term-missing \
  --cov-report=xml:coverage.xml > coverage.txt

if [[ -f coverage.xml ]]; then
  echo "Coverage reports generated: coverage.txt, htmlcov/, coverage.xml"
  python scripts/generate_coverage_report.py $THRESHOLD
else
  echo "coverage.xml not found. Make sure pytest ran successfully."
  exit 1
fi
