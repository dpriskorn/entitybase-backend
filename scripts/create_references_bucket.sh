#!/bin/bash
# Create the S3 buckets for deduplicated references and qualifiers.

set -e

# Bucket names from env or default
REFERENCES_BUCKET="${S3_REFERENCES_BUCKET:-testbucket-references}"
QUALIFIERS_BUCKET="${S3_QUALIFIERS_BUCKET:-testbucket-qualifiers}"

# AWS CLI command to create buckets
# Assuming MinIO or S3 compatible
aws s3 mb "s3://${REFERENCES_BUCKET}" --endpoint-url="${S3_ENDPOINT:-http://minio:9000}" || echo "Bucket ${REFERENCES_BUCKET} already exists or failed to create"
aws s3 mb "s3://${QUALIFIERS_BUCKET}" --endpoint-url="${S3_ENDPOINT:-http://minio:9000}" || echo "Bucket ${QUALIFIERS_BUCKET} already exists or failed to create"

echo "Buckets setup complete: references=${REFERENCES_BUCKET}, qualifiers=${QUALIFIERS_BUCKET}"