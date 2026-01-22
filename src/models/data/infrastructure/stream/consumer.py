from pydantic import BaseModel, ConfigDict


class EntityChangeEventData(BaseModel):
    """Model for entity change events."""

    model_config = ConfigDict(populate_by_name=True)

    entity_id: str
    revision_id: int
    timestamp: str
    user_id: str
    type: str
