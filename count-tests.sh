#!/bin/bash
set -e

echo "# Test Counts"

# Activate virtual environment
source .venv/bin/activate

# Count overall tests using pytest (excludes disabled)
OVERALL=$(pytest --collect-only -q tests/unit tests/integration tests/e2e 2>/dev/null | grep -oP '\d+(?= tests collected)' || echo "0")

# Count test functions by type
UNIT_COUNT=$(grep -r "^def test_" tests/unit/ --include="*.py" | wc -l)
INTEGRATION_COUNT=$(grep -r "^def test_" tests/integration/ --include="*.py" | wc -l)
E2E_COUNT=$(grep -r "^def test_" tests/e2e/ --include="*.py" | wc -l)
DISABLED_COUNT=$(grep -r "^def test_" tests/disabled/ --include="*.py" | wc -l)

echo "- Overall (pytest): $OVERALL"
echo "- Unit: $UNIT_COUNT"
echo "- Integration: $INTEGRATION_COUNT"
echo "- E2E: $E2E_COUNT"
echo "- Disabled: $DISABLED_COUNT"
echo ""
