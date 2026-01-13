"""User activity models."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ActivityType(str, Enum):
    """User activity types for entity operations."""

    ENTITY_CREATE = "entity_create"  # Creating new entities
    ENTITY_EDIT = "entity_edit"  # Editing existing entities
    ENTITY_REVERT = "entity_revert"  # Reverting entity changes
    ENTITY_DELETE = "entity_delete"  # Deleting entities
    ENTITY_UNDELETE = "entity_undelete"  # Undeleting entities
    ENTITY_LOCK = "entity_lock"  # Locking entities
    ENTITY_UNLOCK = "entity_unlock"  # Unlocking entities
    ENTITY_ARCHIVE = "entity_archive"  # Archiving entities
    ENTITY_UNARCHIVE = "entity_unarchive"  # Unarchiving entities


class UserActivityItem(BaseModel):
    """Individual user activity item."""

    id: int
    user_id: int
    activity_type: ActivityType
    entity_id: Optional[str] = Field(default=None)
    revision_id: int = Field(default=0)
    created_at: datetime


class UserActivity(BaseModel):
    """User activity record."""

    id: int
    user_id: int
    activity_type: ActivityType
    entity_id: Optional[str] = Field(default=None)
    revision_id: int = Field(default=0)
    created_at: datetime
