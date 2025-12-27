from pydantic import BaseModel


class S3Config(BaseModel):
    endpoint_url: str
    access_key: str
    secret_key: str
    bucket: str


class SnapshotMetadata(BaseModel):
    key: str


class SnapshotResponse(BaseModel):
    data: str


class SnapshotCreateRequest(BaseModel):
    entity_id: str
    revision_id: int
    data: str
    publication_state: str = "pending"


class SnapshotReadResponse(BaseModel):
    entity_id: str
    revision_id: int
    data: str


class SnapshotUpdateRequest(BaseModel):
    entity_id: str
    revision_id: int
    publication_state: str
