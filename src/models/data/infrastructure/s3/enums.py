from enum import Enum

from pydantic import BaseModel, Field


class EditType(Enum):
    """Enumeration of different types of edits that can be made to entities."""

    LOCK_ADDED = "lock-added"
    LOCK_REMOVED = "lock-removed"
    SEMI_PROTECTION_ADDED = "semi-protection-added"
    SEMI_PROTECTION_REMOVED = "semi-protection-removed"
    MASS_PROTECTION_ADDED = "mass-protection-added"
    MASS_PROTECTION_REMOVED = "mass-protection-removed"
    UNSPECIFIED = "unspecified"
    MANUAL_CREATE = "manual-create"
    MANUAL_UPDATE = "manual-update"
    MANUAL_CORRECTION = "manual-correction"
    REDIRECT_CREATE = "redirect-create"
    REDIRECT_REVERT = "redirect-revert"
    ARCHIVE_ADDED = "archive-added"
    ARCHIVE_REMOVED = "archive-removed"
    SOFT_DELETE = "soft-delete"
    HARD_DELETE = "hard-delete"
    BOT_IMPORT = "bot-import"
    BOT_CLEANUP = "bot-cleanup"
    BOT_MERGE = "bot-merge"
    BOT_SPLIT = "bot-split"
    CLEANUP_2025 = "cleanup-2025"
    CLEANUP_LABELS = "cleanup-labels"
    CLEANUP_DESCRIPTIONS = "cleanup-descriptions"
    MIGRATION_INITIAL = "migration-initial"
    MIGRATION_BATCH = "migration-batch"
    SOFT = "soft-delete"
    HARD = "hard-delete"
    UNDELETE = "undelete"
    MASS_EDIT = "mass-edit"


class DeleteType(str, Enum):
    SOFT = "soft"
    HARD = "hard"


class EntityType(str, Enum):
    """Type of entity.
    UNKNOWN is considered a bug"""

    ITEM = "item"
    PROPERTY = "property"
    LEXEME = "lexeme"
    UNSPECIFIED = "unspecified"
    # ENTITY_SCHEMA = "entityschema"


class MetadataType(str, Enum):
    """Type of metadata stored in S3."""

    LABELS = "labels"
    DESCRIPTIONS = "descriptions"
    ALIASES = "aliases"
    SITELINKS = "sitelinks"
    FORM_REPRESENTATIONS = "form_representations"
    SENSE_GLOSSES = "sense_glosses"


class EditData(BaseModel):
    model_config = {"by_alias": True}

    edit_type: EditType = Field(alias="type", description="Type of edit to be made.")
    user_id: int = Field(description="ID of the user responsible for the edit.")
    is_mass_edit: bool = Field(
        default=False, alias="mass", description="Whether the entity is mass edit."
    )
    edit_summary: str = Field(
        description="Summary of the edit.", max_length=200, alias="summary"
    )
    at: str = Field(description="The date and time of the edit in UTC.")
