from typing import Dict, Any

from pydantic import BaseModel, Field

from models.rest_api.entitybase.response import EntityState
from models.infrastructure.s3.enums import EditType, DeleteType


class EntityCreateRequest(BaseModel):
    """Request model for entity creation."""

    id: str = Field(
        default="",
        description="Entity ID (e.g., Q42) - optional for creation, auto-assigned if not provided",
    )
    type: str = Field(default="item", description="Entity type")
    labels: Dict[str, Dict[str, str]] = {}
    descriptions: Dict[str, Dict[str, str]] = {}
    claims: Dict[str, Any] = {}
    aliases: Dict[str, Any] = {}
    sitelinks: Dict[str, Any] = {}
    is_mass_edit: bool = Field(default=False, description="Whether this is a mass edit")
    edit_type: EditType = Field(
        default=EditType.UNSPECIFIED,
        description="Classification of edit type",
    )
    state: EntityState = Field(default=EntityState(), description="Entity state")
    is_autoconfirmed_user: bool = Field(
        default=False, description="User is autoconfirmed (not a new/unconfirmed account)"
    )
    edit_summary: str = Field(min_length=1, max_length=200, description="Edit summary for this change")
    user_id: int = Field(default=0, description="User who made this change")

    @property
    def data(self) -> Dict[str, Any]:
        return self.model_dump(exclude_unset=True)  # type: ignore[no-any-return]


class EntityUpdateRequest(BaseModel):
    """Request model for updating an entity."""

    id: str = Field(
        ...,
        description="Entity ID (e.g., Q42)",
    )
    type: str = Field(default="item", description="Entity type")
    labels: Dict[str, Dict[str, str]] = {}
    descriptions: Dict[str, Dict[str, str]] = {}
    claims: Dict[str, Any] = {}
    aliases: Dict[str, Any] = {}
    sitelinks: Dict[str, Any] = {}
    is_mass_edit: bool = Field(default=False, description="Whether this is a mass edit")
    state: EntityState = Field(default=EntityState(), description="Entity state")
    edit_type: EditType = Field(
        default=EditType.UNSPECIFIED,
        description="Classification of edit type",
    )
    is_not_autoconfirmed_user: bool = Field(
        default=False, description="User is not autoconfirmed (new/unconfirmed account)"
    )
    edit_summary: str = Field(min_length=1, description="Edit summary for this change")
    user_id: int = Field(default=0, description="User who made this change")

    @property
    def data(self) -> Dict[str, Any]:
        return self.model_dump(exclude_unset=True)  # type: ignore[no-any-return]


class EntityDeleteRequest(BaseModel):
    """Request to delete an entity."""

    delete_type: DeleteType = Field(description="Type of deletion")
    entity_id: str = Field(min_length=1, description="ID of the entity to delete")
    edit_summary: str = Field(min_length=1, description="Edit summary for this change")
    user_id: int = Field(default=0, description="User who made this change")

    @property
    def data(self) -> Dict[str, Any]:
        return self.model_dump(exclude_unset=True)  # type: ignore[no-any-return]


class EntityInsertDataRequest(BaseModel):
    """Data for inserting a revision."""

    is_mass_edit: bool
    edit_type: str
    statements: list[int] | None
    properties: list[str] | None
    property_counts: dict[str, int] | None
