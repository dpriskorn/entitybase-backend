#!/bin/bash
set -Eeuo pipefail

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
  #--cov-report=html \
  --cov-report=xml \
  > coverage.txt 2>&1

if [ -f \"coverage.xml\" ]; then
    echo \"Coverage reports generated: coverage.txt, htmlcov/, coverage.xml\"
    echo \"Generating coverage badge and missing coverage report...\"
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

# Generate missing coverage report
threshold = $THRESHOLD / 100.0
missing_files = []
for class_elem in root.findall('.//class'):
    filename = class_elem.attrib.get('filename', 'Unknown')
    line_rate = float(class_elem.attrib.get('line-rate', 0))
    if line_rate < threshold:
        missing_files.append((filename, line_rate * 100))

filename = 'coverage_below_threshold.txt'
with open(filename, 'w') as f:
    f.write(f'Files with coverage below {THRESHOLD}%:\\n')
    if missing_files:
        for filename, pct in sorted(missing_files, key=lambda x: x[1]):
            f.write(f'{filename}: {pct:.1f}%\\n')
    else:
        f.write('None\\n')

print(f'Missing coverage report saved to {filename}')
"
else
    echo "coverage.xml not found. Make sure coverage ran successfully."
fi