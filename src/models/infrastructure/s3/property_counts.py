"""Property counts model."""

from pydantic import BaseModel, Field


class PropertyCounts(BaseModel):
    """Model for property statement counts."""

    counts: dict[str, int] = Field(
        default_factory=dict,
        description="Dictionary mapping property ID to statement count",
    )
