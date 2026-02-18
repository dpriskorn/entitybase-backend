from pydantic import BaseModel, Field


class EntityStatusRequest(BaseModel):
    """Request model for entity status changes (lock, archive, semi-protect)."""

    model_config = {"extra": "forbid"}

    edit_summary: str | None = Field(default=None, max_length=200)
