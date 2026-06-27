"""S3 connection management and client handling."""

import logging
from typing import Any

from minio import Minio
from pydantic import Field

from models.infrastructure.connection import ConnectionManager
from models.data.config.s3 import S3Config

logger = logging.getLogger(__name__)


class S3ConnectionManager(ConnectionManager):
    """Handles S3 connection and healthcheck."""

    config: S3Config
    minio_client: Any = Field(default=None, exclude=True)

    def connect(self) -> None:
        """Establish S3 client connection."""
        if self.minio_client is None:
            endpoint = self.config.endpoint_url
            if endpoint.startswith("http://"):
                endpoint = endpoint[7:]
            elif endpoint.startswith("https://"):
                endpoint = endpoint[8:]
            if "/" in endpoint:
                endpoint = endpoint.split("/")[0]
            self.minio_client = Minio(
                endpoint,
                access_key=self.config.access_key,
                secret_key=self.config.secret_key,
                secure=False,
            )

    @property
    def healthy_connection(self) -> bool:
        """Check if S3 connection is healthy.

        Returns:
            True if connection is healthy, False otherwise.
        """
        # noinspection PyBroadException
        logger.debug("Checking if S3 connection is healthy")
        logger.debug(self.config.model_dump(mode="json"))
        try:
            self.connect()
            if self.minio_client is not None:
                return self.minio_client.bucket_exists(self.config.bucket)
            return False
        except Exception as e:
            logger.error(e)
            return False
