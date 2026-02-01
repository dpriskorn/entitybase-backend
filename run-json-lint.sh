#!/bin/bash
set -e

echo "Running JSON lint: Detecting json.dumps usage and recommending model_dump(mode='json')"

ALLOWLIST_FILE="config/linters/allowlists/custom/json-dumps.txt"

# Read allowlist and build exclude patterns
ALLOWLIST_ENTRIES=""
if [ -f "$ALLOWLIST_FILE" ]; then
    echo "Using allowlist: $ALLOWLIST_FILE"
    ALLOWLIST_ENTRIES=$(grep -v "^#" "$ALLOWLIST_FILE" | grep -v "^$")
else
    echo "Warning: Allowlist file not found: $ALLOWLIST_FILE"
fi

# Find all json.dumps uses
grep_output=$(grep -r "json.dumps" src/ --include="*.py" -n 2>/dev/null || true)

# Filter out violations
violations=""
while IFS= read -r line; do
    if [ -z "$line" ]; then
        continue
    fi

    # Skip if already uses model_dump(mode='json')
    if echo "$line" | grep -q "model_dump(mode=\"json\")"; then
        continue
    fi
    if echo "$line" | grep -q "model_dump(mode='json')"; then
        continue
    fi

    # Parse line: get filepath:linenum
    filepath=$(echo "$line" | cut -d: -f1)
    linenum=$(echo "$line" | cut -d: -f2)

    # Check if this entry is in the allowlist
    if [ -n "$ALLOWLIST_ENTRIES" ]; then
        if echo "$ALLOWLIST_ENTRIES" | grep -q "^${filepath}:${linenum}$"; then
            continue
        fi
    fi

    violations="$violations\n$line"
done <<< "$grep_output"

if [ -n "$violations" ]; then
    # Count violations (excluding empty lines)
    count=$(echo -e "$violations" | grep -c "." || true)
    echo "Found $count potentially problematic json.dumps usage:"
    echo ""
    echo -e "$violations"
    echo ""
    echo "Consider replacing json.dumps(model.model_dump()) with json.dumps(model.model_dump(mode='json')) for better JSON serialization."
    echo "If this is a false positive, add it to $ALLOWLIST_FILE"
    exit 1
else
    echo "No json.dumps violations found (all uses correctly use model_dump(mode='json') or are allowlisted)."
fi