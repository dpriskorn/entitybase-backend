"""Request models for endorsement operations."""

from pydantic import BaseModel, Field


class EndorsementListRequest(BaseModel):
    """Request to filter endorsement lists."""

    limit: int = Field(50, ge=1, le=500, description="Maximum number of endorsements to return")
    offset: int = Field(0, ge=0, description="Number of endorsements to skip")
    include_removed: bool = Field(False, description="Include withdrawn endorsements")