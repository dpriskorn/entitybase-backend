from typing import Any
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from pydantic import BaseModel, Field

from services.shared.models.s3_models import (
    S3Config,
    SnapshotMetadata,
    SnapshotCreateRequest,
    SnapshotReadResponse,
    SnapshotUpdateRequest
)


class S3Client(BaseModel):
    config: S3Config
    client: Any = Field(default=None, exclude=True)
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, config: S3Config, **kwargs):
        super().__init__(config=config, **kwargs)
        self.client = boto3.client(
            "s3",
            endpoint_url=config.endpoint_url,
            aws_access_key_id=config.access_key,
            aws_secret_access_key=config.secret_key,
            config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
            region_name="us-east-1"
        )
        
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        try:
            self.client.head_bucket(Bucket=self.config.bucket)
        except ClientError as e:
            if e.response['Error']['Code'] == '404' or e.response['Error']['Code'] == 'NoSuchBucket':
                try:
                    self.client.create_bucket(Bucket=self.config.bucket)
                except ClientError as ce:
                    print(f"Error creating bucket {self.config.bucket}: {ce}")
                    raise
            else:
                print(f"Error checking bucket {self.config.bucket}: {e}")
                raise
        except Exception as e:
            print(f"Unexpected error checking/creating bucket {self.config.bucket}: {e}")
            raise
    
    def write_snapshot(self, request: SnapshotCreateRequest) -> SnapshotMetadata:
        import json
        key = f"{request.entity_id}/r{request.revision_id}.json"
        self.client.put_object(
            Bucket=self.config.bucket,
            Key=key,
            Body=json.dumps(request.data),
            Metadata={"publication_state": request.publication_state}
        )
        return SnapshotMetadata(key=key)
    
    def read_snapshot(self, entity_id: str, revision_id: int) -> SnapshotReadResponse:
        key = f"{entity_id}/r{revision_id}.json"
        response = self.client.get_object(Bucket=self.config.bucket, Key=key)
        return SnapshotReadResponse(
            entity_id=entity_id,
            revision_id=revision_id,
            data=response["Body"].read().decode("utf-8")
        )
    
    def mark_published(self, request: SnapshotUpdateRequest) -> None:
        key = f"{request.entity_id}/r{request.revision_id}.json"
        self.client.copy_object(
            Bucket=self.config.bucket,
            CopySource={"Bucket": self.config.bucket, "Key": key},
            Key=key,
            Metadata={"publication_state": request.publication_state},
            MetadataDirective="REPLACE"
        )
