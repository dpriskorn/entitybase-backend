import boto3
from botocore.client import BaseClient
from botocore.config import Config

from models.infrastructure.connection import ConnectionManager
from models.s3_models import S3Config


class S3ConnectionManager(ConnectionManager):
    """Handles S3 connection and healthcheck"""

    config: S3Config
    conn: BaseClient | None = None

    def connect(self) -> None:
        if self.conn is None:
            self.conn = boto3.client(
                "s3",
                endpoint_url=self.config.endpoint_url,
                aws_access_key_id=self.config.access_key,
                aws_secret_access_key=self.config.secret_key,
                config=Config(
                    signature_version="s3v4", s3={"addressing_style": "path"}
                ),
                region_name="us-east-1",
            )

    @property
    def healthy_connection(self) -> bool:
        """Check if S3 connection is healthy

        Returns:
            True if connection is healthy, False otherwise
        """
        # noinspection PyBroadException
        try:
            self.connect()
            if self.conn:
                self.conn.head_bucket(Bucket=self.config.bucket)
                return True
            return False
        except Exception:
            return False
