from pydantic import BaseModel


class VitessConfig(BaseModel):
    host: str
    port: int
    database: str
    user: str = "root"
    password: str = ""


class RegisterEntityRequest(BaseModel):
    external_id: str
    internal_id: int


class RegisterEntityResponse(BaseModel):
    success: bool


class GetHeadRequest(BaseModel):
    entity_id: int


class GetHeadResponse(BaseModel):
    head_revision_id: int | None


class CASUpdateHeadRequest(BaseModel):
    entity_id: int
    old_revision_id: int | None
    new_revision_id: int


class InsertRevisionRequest(BaseModel):
    entity_id: int
    revision_id: int


class GetHistoryRequest(BaseModel):
    entity_id: int


class HistoryRecord(BaseModel):
    revision_id: int
    created_at: str
