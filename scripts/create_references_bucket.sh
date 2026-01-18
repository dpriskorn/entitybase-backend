#!/bin/bash
# Create the references S3 bucket for deduplicated references.

set -e

# Bucket name from env or default
BUCKET_NAME="${S3_REFERENCES_BUCKET:-testbucket-references}"

# AWS CLI command to create bucket
# Assuming MinIO or S3 compatible
aws s3 mb "s3://${BUCKET_NAME}" --endpoint-url="${S3_ENDPOINT:-http://minio:9000}" || echo "Bucket ${BUCKET_NAME} already exists or failed to create"

echo "References bucket setup complete: ${BUCKET_NAME}"