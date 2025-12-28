from typing import Any, Dict
from pydantic import BaseModel


class S3Config(BaseModel):
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
