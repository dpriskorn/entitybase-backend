#!/bin/bash
set -Eeuo pipefail

# Check if Docker is available and we're in a Docker environment
if command -v docker &> /dev/null && [ -f "docker/docker-compose.yml" ]; then
    echo "Running coverage in Docker container..."
    cd docker
    docker-compose run --rm coverage
    echo "Coverage reports generated in htmlcov/ and coverage.xml"
else
    echo "Docker not available, running coverage locally..."
    source .venv/bin/activate

    echo "Running tests with coverage..."
    python -m pytest --cov=src --cov-report=term-missing --cov-report=html:htmlcov --cov-report=xml:coverage.xml
fi

if [ -f "coverage.xml" ]; then
    echo "Generating coverage badge..."
    python -c "
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