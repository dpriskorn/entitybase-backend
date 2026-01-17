#!/bin/bash
#set -Eeuo pipefail

# Adjustable threshold for missing coverage report (percentage)
THRESHOLD=50

source .venv/bin/activate

echo \"Running unit tests with coverage...\"
cd /home/dpriskorn/src/python/wikibase-backend
export PYTHONPATH=src
pytest \
  -m "unit" \
  --cov=src \
  --cov-report=term-missing \
  --cov-report=xml \
  > coverage.txt 2>&1

if [ -f \"coverage.xml\" ]; then
    echo \"Coverage reports generated: coverage.txt, htmlcov/, coverage.xml\"
    echo \"Generating coverage badge and missing coverage report...\"
    python scripts/generate_coverage_report.py $THRESHOLD
else
    echo "coverage.xml not found. Make sure coverage ran successfully."
fi