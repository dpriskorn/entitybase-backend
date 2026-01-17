#!/bin/bash
#set -Eeuo pipefail

# Adjustable threshold for missing coverage report (percentage)
THRESHOLD=50

source .venv/bin/activate

echo \"Running unit tests with coverage...\"
cd /home/dpriskorn/src/python/wikibase-backend
export PYTHONPATH=src
coverage run --source=src -m pytest \
  -m "unit" \
  --cov-report=term-missing \
  > coverage.txt 2>&1
coverage xml

if ls coverage.xml > /dev/null 2>&1 ; then
    echo \"Coverage reports generated: coverage.txt, htmlcov/, coverage.xml\"
    echo \"Generating coverage badge and missing coverage report...\"
    python scripts/generate_coverage_report.py $THRESHOLD
else
    echo "coverage.xml not found. Make sure coverage ran successfully."
fi