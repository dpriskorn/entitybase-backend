"""Entity listing response models."""

from pydantic import BaseModel, Field


class EntityListing(BaseModel):
    """Model for entity listing entries."""

    entity_id: str = Field(..., description="Entity ID")
    entity_type: str = Field(..., description="Entity type (Q, P, etc.)")
    reason: str = Field(default="", description="Reason for listing")