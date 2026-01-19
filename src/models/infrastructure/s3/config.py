"""S3 configuration model."""

from pydantic import BaseModel


class S3Config(BaseModel):
    """Configuration for S3 connections."""

    endpoint_url: str
    access_key: str
    secret_key: str