"""S3 connection management and client handling."""

import boto3  # type: ignore[import-untyped]
from botocore.config import Config  # type: ignore[import-untyped]
from mypy_boto3_s3.client import S3Client
from pydantic import BaseModel, Field


class S3DictModel(BaseModel):
    addressing_style: str


from models.infrastructure.connection import ConnectionManager
from models.s3_models import S3Config


class S3ConnectionManager(ConnectionManager):
    """Handles S3 connection and healthcheck."""

    config: S3Config
    boto_client: S3Client | None = Field(default=None, exclude=True)

    def connect(self) -> None:
        """Establish S3 client connection."""
        if self.boto_client is None:
            self.boto_client = boto3.client(
                "s3",
                endpoint_url=self.config.endpoint_url,
                aws_access_key_id=self.config.access_key,
                aws_secret_access_key=self.config.secret_key,
                config=Config(
                    signature_version="s3v4",
                    s3=S3DictModel(addressing_style="path").model_dump(),  # type: ignore[arg-type]
                ),
                region_name="us-east-1",
            )

    @property
    def healthy_connection(self) -> bool:
        """Check if S3 connection is healthy.

        Returns:
            True if connection is healthy, False otherwise.
        """
        # noinspection PyBroadException
        try:
            self.connect()
            if self.boto_client is not None:
                self.boto_client.head_bucket(Bucket=self.config.bucket)  # type: ignore[attr-defined]
                return True
            return False
        except Exception:
            return False
