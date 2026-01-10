from typing import Any, Dict

from pydantic import BaseModel

from models.api import StatementResponse
from models.infrastructure.config import Config


class S3Config(Config):
    endpoint_url: str
    access_key: str
    secret_key: str
    bucket: str


class RevisionMetadata(BaseModel):
    key: str


class RevisionReadResponse(BaseModel):
    entity_id: str
    revision_id: int
    data: Dict[str, Any]


class StoredStatement(StatementResponse):
    """Statement format for S3 storage.

    Subclass of StatementResponse to ensure compatibility with API responses.
    Adds no additional fields, maintains same structure.
    """

    pass
