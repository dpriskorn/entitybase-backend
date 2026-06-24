#!/bin/bash
# Setup script for creating rustfs buckets for Wikibase development

set -e

# Configuration - can be overridden with environment variables
RUSTFS_ENDPOINT=${RUSTFS_ENDPOINT:-http://localhost:9000}
RUSTFS_ACCESS_KEY=${RUSTFS_ACCESS_KEY:-minioadmin}
RUSTFS_SECRET_KEY=${RUSTFS_SECRET_KEY:-minioadmin}

# Bucket names
BUCKETS=("terms" "statements" "revisions" "dumps")

echo "Setting up rustfs buckets for Wikibase development..."
echo "rustfs Endpoint: $RUSTFS_ENDPOINT"
echo "Buckets: ${BUCKETS[*]}"
echo

# Check if aws CLI is installed
if ! command -v aws &> /dev/null; then
    echo "Error: AWS CLI is not installed."
    echo "Install it from: https://aws.amazon.com/cli/"
    exit 1
fi

# Create buckets
echo "Creating buckets..."
for bucket in "${BUCKETS[@]}"; do
    echo -n "Creating bucket: $bucket ... "
    if aws s3 mb "s3://$bucket" \
        --endpoint-url="$RUSTFS_ENDPOINT" \
        --region us-east-1 \
        2>/dev/null; then
        echo "✓"
    else
        echo "✗ Failed (may already exist)"
    fi
done

echo
echo "All buckets created!"
echo
echo "Bucket list:"
for bucket in "${BUCKETS[@]}"; do
    echo "  - $bucket"
done

echo
echo "You can now use the buckets with the following endpoints:"
echo "  Terms: $RUSTFS_ENDPOINT/terms"
echo "  Statements: $RUSTFS_ENDPOINT/statements"
echo "  Revisions: $RUSTFS_ENDPOINT/revisions"
echo "  Dumps: $RUSTFS_ENDPOINT/dumps"
echo
echo "Setup complete!"
