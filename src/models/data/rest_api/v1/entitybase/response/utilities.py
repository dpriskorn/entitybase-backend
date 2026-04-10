"""Generic utility response models."""

from pydantic import BaseModel, Field


class DeleteResponse(BaseModel):
    """Response for DELETE operations."""

    success: bool = Field(description="Whether the operation succeeded.")


class VersionResponse(BaseModel):
    """Response model for version endpoint."""

    api_version: str = Field(description="API version")
    entitybase_version: str = Field(description="EntityBase version")


class UptimeResponse(BaseModel):
    """Response model for uptime endpoint."""

    start_time: str = Field(
        description="Application startup timestamp in ISO 8601 format"
    )
    uptime_seconds: int = Field(description="Seconds since application startup")
