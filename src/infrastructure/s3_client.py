import boto3
from botocore.client import Config


class S3Client:
    def __init__(self, endpoint_url: str, access_key: str, secret_key: str, bucket: str):
        self.bucket = bucket
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version="s3v4"),
            region_name="us-east-1"
        )

    def write_snapshot(self, entity_id: str, revision_id: int, data: str, tags: dict | None = None) -> str:
        if tags is None:
            tags = {}
        key = f"{entity_id}/r{revision_id}.json"
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=data,
            Metadata={"publication_state": tags.get("publication_state", "pending")}
        )
        return key

    def read_snapshot(self, entity_id: str, revision_id: int) -> str:
        key = f"{entity_id}/r{revision_id}.json"
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        return response["Body"].read().decode("utf-8")

    def mark_published(self, entity_id: str, revision_id: int) -> None:
        key = f"{entity_id}/r{revision_id}.json"
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        self.client.copy_object(
            Bucket=self.bucket,
            CopySource={"Bucket": self.bucket, "Key": key},
            Key=key,
            Metadata={"publication_state": "published"},
            MetadataDirective="REPLACE"
        )
