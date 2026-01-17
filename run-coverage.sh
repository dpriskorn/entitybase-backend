#!/bin/bash
set -Eeuo pipefail

source .venv/bin/activate

echo \"Running unit tests with coverage...\"
cd /home/dpriskorn/src/python/wikibase-backend
export PYTHONPATH=src
python -m pytest \
  --cov=src --cov-report=term-missing \
  --cov-report=txt:coverage.txt \
  #--cov-report=html \
  --cov-report=xml \
  --ignore=tests/disabled/ \
  tests/unit/

if [ -f \"coverage.xml\" ]; then
    echo \"Coverage reports generated: coverage.txt, htmlcov/, coverage.xml\"
    echo \"Generating coverage badge...\"
    python -c \"
import xml.etree.ElementTree as ET
import re

# Parse coverage.xml
tree = ET.parse('coverage.xml')
root = tree.getroot()

# Get coverage percentage
coverage = float(root.attrib['line-rate']) * 100

# Generate badge URL
color = 'red' if coverage < 50 else 'orange' if coverage < 75 else 'yellow' if coverage < 90 else 'green'
badge_url = f'https://img.shields.io/badge/coverage-{coverage:.1f}%25-{color}'

print(f'Coverage: {coverage:.1f}%')
print(f'Badge URL: {badge_url}')
"
else
    echo "coverage.xml not found. Make sure coverage ran successfully."
fi