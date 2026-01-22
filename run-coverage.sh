#!/bin/bash
# set -euo pipefail

THRESHOLD=50

source .venv/bin/activate

cd /home/dpriskorn/src/python/wikibase-backend
export PYTHONPATH=src

echo "Running unit tests with coverage..."

# Cleanup first
rm coverage_below_threshold.txt
rm coverage.txt
rm coverage.xml
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# Test
pytest \
  -m "unit" \
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
