"""Request models for thanks operations."""

from pydantic import BaseModel, Field


class ThanksListRequest(BaseModel):
    """Request to filter thanks lists."""

    limit: int = Field(
        50, ge=1, le=500, description="Maximum number of thanks to return"
    )
    offset: int = Field(0, ge=0, description="Number of thanks to skip")
    hours: int = Field(24, ge=1, le=720, description="Time span in hours")
