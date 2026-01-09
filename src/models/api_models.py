from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class EditType(Enum):
    """Enumeration of different types of edits that can be made to entities."""

    UNSPECIFIED = "unspecified"
    MANUAL_CREATE = "manual-create"
    MANUAL_UPDATE = "manual-update"
    MANUAL_CORRECTION = "manual-correction"
    REDIRECT_CREATE = "redirect-create"
    REDIRECT_REVERT = "redirect-revert"
    ARCHIVE_ADDED = "archive-added"
    ARCHIVE_REMOVED = "archive-removed"
    LOCK_ADDED = "lock-added"
    LOCK_REMOVED = "lock-removed"
    SOFT_DELETE = "soft-delete"
    HARD_DELETE = "hard-delete"
    BOT_IMPORT = "bot-import"
    BOT_CLEANUP = "bot-cleanup"
    BOT_MERGE = "bot-merge"
    BOT_SPLIT = "bot-split"
    MIGRATION_INITIAL = "migration-initial"
    MIGRATION_BATCH = "migration-batch"


class ItemCreateRequest(BaseModel):
    """Request model for creating a new Wikibase item."""

    type: str = Field(default="item", description="Entity type (must be 'item')")
    labels: Optional[Dict[str, Dict[str, str]]] = None
    descriptions: Optional[Dict[str, Dict[str, str]]] = None
    claims: Optional[Dict[str, Any]] = None
    aliases: Optional[Dict[str, Any]] = None
    sitelinks: Optional[Dict[str, Any]] = None
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
    def data(self) -> Dict[str, Any]:
        return self.model_dump(exclude_unset=True)


class ItemUpdateRequest(BaseModel):
    """Request model for updating an existing Wikibase item."""

    type: str = Field(default="item", description="Entity type (must be 'item')")
    labels: Optional[Dict[str, Dict[str, str]]] = None
    descriptions: Optional[Dict[str, Dict[str, str]]] = None
    claims: Optional[Dict[str, Any]] = None
    aliases: Optional[Dict[str, Any]] = None
    sitelinks: Optional[Dict[str, Any]] = None
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
    def data(self) -> Dict[str, Any]:
        return self.model_dump(exclude_unset=True)
