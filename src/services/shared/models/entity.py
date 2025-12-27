from pydantic import BaseModel
from typing import Any, Dict


class EntityCreateRequest(BaseModel):
    data: Dict[str, Any]


class EntityResponse(BaseModel):
    id: str
    revision_id: int
    data: Dict[str, Any]


class RevisionMetadata(BaseModel):
    revision_id: int
    created_at: str
