"""S3 configuration model."""

from models.infrastructure.config import Config


class S3Config(Config):
    """Configuration for S3 connections."""

    endpoint_url: str
    access_key: str
    secret_key: str
    bucket: str
    region: str
