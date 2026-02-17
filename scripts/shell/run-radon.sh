#!/bin/bash
cd "$(dirname "$0")/../.."
source .venv/bin/activate

COMPLEXITY_THRESHOLD=20

echo "=== Radon Complexity Check (threshold $COMPLEXITY_THRESHOLD) ==="
OUTPUT=$(poetry run radon cc -a -s src/ 2>&1)

# Filter output to show only items with complexity >= 3
FILTERED_OUTPUT=$(echo "$OUTPUT" | grep -E "\( [3-9]|\(1[0-9]|\(2[0-9]+\)" || true)
echo "$FILTERED_OUTPUT"

# Show average complexity line
echo "$OUTPUT" | grep -E "Average"

# Parse output and check for functions with complexity > threshold
# Grade mapping: A=0-10, B=11-20, C=21-30, D=31-40, F=41+
# With threshold 20, only fail on grades D, E, F (complexity > 20)
HIGH_COMPLEXITY=$(echo "$OUTPUT" | grep -E " - [DEF]" | grep -v "Average" || true)
if [ -n "$HIGH_COMPLEXITY" ]; then
    echo ""
    echo "❌ Functions with complexity > $COMPLEXITY_THRESHOLD (grades C, D, F) found:"
    echo "$HIGH_COMPLEXITY"
    echo ""
    echo "⚠️  To allowlist this, add the function/class name to config/linters/allowlists/radon.txt"
    exit 1
fi

echo ""
echo "=== Duplicate Method Check ==="
python scripts/run-radon.py