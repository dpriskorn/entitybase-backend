from pydantic import BaseModel, ConfigDict, Field


class EntityChangeEventData(BaseModel):
    """Model for entity change events."""

    model_config = ConfigDict(populate_by_name=True)

    entity_id: str = Field(alias="id")
    revision_id: int = Field(alias="rev")
    change_type: str = Field(alias="type")
    from_revision_id: int | None = Field(default=None, alias="from_rev")
    timestamp: str = Field(alias="at")
    user_id: str = Field(alias="user")
    edit_summary: str = Field(default="", alias="summary")
