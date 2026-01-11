#!/bin/bash
# Setup script for creating MinIO buckets for Wikibase development

set -e

# Configuration - can be overridden with environment variables
MINIO_ALIAS=${MINIO_ALIAS:-wikibase-dev}
MINIO_ENDPOINT=${MINIO_ENDPOINT:-http://localhost:9000}
MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY:-minioadmin}
MINIO_SECRET_KEY=${MINIO_SECRET_KEY:-minioadmin}

# Bucket names
BUCKETS=("terms" "statements" "revisions" "dumps")

echo "Setting up MinIO buckets for Wikibase development..."
echo "MinIO Endpoint: $MINIO_ENDPOINT"
echo "Alias: $MINIO_ALIAS"
echo "Buckets: ${BUCKETS[*]}"
echo

# Check if mc (MinIO client) is installed
if ! command -v mc &> /dev/null; then
    echo "Error: MinIO client (mc) is not installed."
    echo "Install it from: https://min.io/download"
    echo "Or use: wget https://dl.min.io/client/mc/release/linux-amd64/mc && chmod +x mc && sudo mv mc /usr/local/bin/"
    exit 1
fi

# Configure MinIO client
echo "Configuring MinIO client..."
mc alias set $MINIO_ALIAS $MINIO_ENDPOINT $MINIO_ACCESS_KEY $MINIO_SECRET_KEY

# Test connection
echo "Testing connection..."
if ! mc admin info $MINIO_ALIAS &> /dev/null; then
    echo "Error: Cannot connect to MinIO at $MINIO_ENDPOINT"
    echo "Make sure MinIO is running and credentials are correct."
    exit 1
fi

echo "Connection successful!"
echo

# Create buckets
echo "Creating buckets..."
for bucket in "${BUCKETS[@]}"; do
    echo -n "Creating bucket: $bucket ... "
    if mc mb $MINIO_ALIAS/$bucket --ignore-existing; then
        echo "✓"
    else
        echo "✗ Failed"
        exit 1
    fi
done

echo
echo "All buckets created successfully!"
echo
echo "Bucket list:"
for bucket in "${BUCKETS[@]}"; do
    echo "  - $bucket"
done

echo
echo "You can now use the buckets with the following endpoints:"
echo "  Terms: $MINIO_ENDPOINT/$MINIO_ALIAS/terms"
echo "  Statements: $MINIO_ENDPOINT/$MINIO_ALIAS/statements"
echo "  Revisions: $MINIO_ENDPOINT/$MINIO_ALIAS/revisions"
echo "  Dumps: $MINIO_ENDPOINT/$MINIO_ALIAS/dumps"
echo
echo "Setup complete! 🎉"