from typing import Dict, Any

from pydantic import BaseModel, Field

from models.rest_api.misc import EditType, DeleteType


class EntityCreateRequest(BaseModel):
    """Request model for entity creation."""

    id: str = Field(..., description="Entity ID (e.g., Q42)")
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
    is_semi_protected: bool = Field(default=False, description="Item is semi-protected")
    is_locked: bool = Field(default=False, description="Item is locked from edits")
    is_archived: bool = Field(default=False, description="Item is archived")
    is_dangling: bool = Field(
        default=False,
        description="Item has no maintaining WikiProject (computed by frontend)",
    )
    is_mass_edit_protected: bool = Field(
        default=False, description="Item is protected from mass edits"
    )
    is_not_autoconfirmed_user: bool = Field(
        default=False, description="User is not autoconfirmed (new/unconfirmed account)"
    )
    edit_summary: str = Field(min_length=1, description="Edit summary for this change")
    editor: str = Field(default="", description="Editor who made this change")

    @property
    def data(self) -> Dict[str, Any]:
        return self.model_dump(exclude_unset=True)


class EntityDeleteRequest(BaseModel):
    """Request to delete an entity."""

    delete_type: DeleteType = Field(description="Type of deletion")
    entity_id: str = Field(description="ID of the entity to delete")
    edit_summary: str = Field(min_length=1, description="Edit summary for this change")
    editor: str = Field(default="", description="Editor who made this change")

    @property
    def data(self) -> Dict[str, Any]:
        return self.model_dump(exclude_unset=True)


class RevisionInsertDataRequest(BaseModel):
    """Data for inserting a revision."""

    is_mass_edit: bool
    edit_type: str
    statements: list[int] | None
    properties: list[str] | None
    property_counts: dict[str, int] | None
