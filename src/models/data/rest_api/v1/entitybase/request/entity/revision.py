from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field

from models.data.infrastructure.s3.enums import EntityType
from models.data.rest_api.v1.entitybase.response.statement import StatementHashResult


class CreateRevisionRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    entity_id: str = Field(..., description="Entity identifier")
    new_revision_id: int = Field(..., description="New revision ID to create")
    head_revision_id: int = Field(..., description="Current head revision ID")
    request_data: Dict[str, Any] = Field(..., description="Full entity data for revision")
    entity_type: EntityType = Field(..., description="Type of entity (item, property, etc.)")
    hash_result: StatementHashResult = Field(..., description="Processed statement hashes")
    is_mass_edit: bool = Field(default=False, description="Whether this is a mass edit")
    edit_type: Any = Field(..., description="Type of edit operation")
    edit_summary: str = Field(default="", description="Edit summary text")
    is_semi_protected: bool = Field(default=False, description="Entity is semi-protected")
    is_locked: bool = Field(default=False, description="Entity is locked")
    is_archived: bool = Field(default=False, description="Entity is archived")
    is_dangling: bool = Field(default=False, description="Entity is dangling")
    is_mass_edit_protected: bool = Field(default=False, description="Entity is mass edit protected")
    is_creation: bool = Field(default=False, description="Whether this is a creation operation")
    user_id: int = Field(default=0, description="User ID creating the revision")