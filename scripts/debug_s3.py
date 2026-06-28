#!/usr/bin/env python3
import os
from models.config.settings import settings

print(f"S3_ENDPOINT env: {os.environ.get('S3_ENDPOINT', 'NOT SET')}")
print(f"S3_ENDPOINT from settings: {settings.s3_endpoint}")
print(f"S3_ACCESS_KEY env: {os.environ.get('S3_ACCESS_KEY', 'NOT SET')}")
print(f"S3_SECRET_KEY env: {os.environ.get('S3_SECRET_KEY', 'NOT SET')}")
print(f"S3_BUCKET env: {os.environ.get('S3_BUCKET', 'NOT SET')}")

s3_config = settings.get_s3_config
endpoint = s3_config.endpoint_url
print(f"S3Config endpoint_url: {endpoint}")
print(f"S3Config bucket: {s3_config.bucket}")

# Remove http:// or https:// prefix since Minio adds it based on secure parameter
if endpoint.startswith("http://"):
    endpoint = endpoint[7:]
elif endpoint.startswith("https://"):
    endpoint = endpoint[8:]
print(f"Endpoint after stripping scheme: {endpoint}")

from minio import Minio
client = Minio(
    endpoint,
    s3_config.access_key,
    s3_config.secret_key,
    secure=False,
)
buckets = client.list_buckets()
print(f"Buckets: {[b.name for b in buckets]}")
