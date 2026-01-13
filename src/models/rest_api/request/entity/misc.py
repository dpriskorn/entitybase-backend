from typing import Any, Dict, Optional


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
    edit_summary: str = Field(default="", description="Edit summary for this change")
    editor: str = Field(default="", description="Editor who made this change")

    @property
    def data(self) -> Any:
        return self.model_dump(exclude_unset=True)


class EntityDeleteRequest(BaseModel):
    delete_type: DeleteType = Field(
        default=DeleteType.SOFT, description="Type of deletion"
    )
    is_locked: bool = Field(default=False, description="User has lock permission")
    edit_summary: str = Field(default="", description="Edit summary for deletion")
    editor: str = Field(default="", description="Editor who performed deletion")
    bot: bool = Field(default=False, description="Whether this was a bot edit")


class EntityRedirectRequest(BaseModel):
    redirect_from_id: str = Field(
        ..., description="Source entity ID to be marked as redirect (e.g., Q59431323)"
    )
    redirect_to_id: str = Field(..., description="Target entity ID (e.g., Q42)")
    created_by: str = Field(
        default="rest-api", description="User or system creating redirect"
    )


class EntityUpdateRequest(BaseModel):
    """Request model for updating an entity."""

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
    edit_summary: str = Field(default="", description="Edit summary for this change")
    editor: str = Field(default="", description="Editor who made this change")

    @property
    def data(self) -> Any:
        return self.model_dump(exclude_unset=True)


class EntityJsonImportRequest(BaseModel):
    """Request model for importing entities from Wikidata JSONL dump."""

    jsonl_file_path: str = Field(
        ..., description="Path to JSONL file containing Wikidata entities"
    )
    start_line: int = Field(
        default=2, description="Starting line number (default 2, skips header)"
    )
    end_line: Optional[int] = Field(
        default=None, description="Ending line number (None = to end)"
    )
    overwrite_existing: bool = Field(
        default=False, description="Whether to overwrite existing entities"
    )
    worker_id: Optional[str] = Field(
        default=None, description="Worker identifier for logging"
    )


class RevisionInsertDataRequest(BaseModel):
    """Data for inserting a revision."""

    is_mass_edit: bool
    edit_type: str
    statements: list[int] | None
    properties: list[str] | None
    property_counts: dict[str, int] | None
