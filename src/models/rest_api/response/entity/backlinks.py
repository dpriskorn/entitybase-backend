from pydantic import BaseModel, Field

class Backlink(BaseModel):
    """Model representing a backlink from one entity to another."""

    entity_id: str = Field(description="Entity ID that references the target")
    property_id: str = Field(description="Property used in the reference")
    rank: str = Field(description="Rank of the statement (normal/preferred/deprecated)")


class BacklinksResponse(BaseModel):
    """Response model for backlinks API."""

    backlinks: list[Backlink] = Field(description="List of backlinks")
    limit: int = Field(description="Requested limit")
    offset: int = Field(description="Requested offset")
