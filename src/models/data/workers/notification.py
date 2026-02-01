"""Data models for watchlist notifications."""

from pydantic import BaseModel

from models.data.workers.changed_properties import ChangedProperties


class NotificationData(BaseModel):
    """Model for notification data when creating user notifications."""

    entity_id: str
    revision_id: int
    change_type: str
    changed_properties: ChangedProperties | None = None
    event_timestamp: str = ""