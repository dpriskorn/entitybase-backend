"""Generic utility response models."""

from pydantic import BaseModel, Field


class DeleteResponse(BaseModel):
    """Response for DELETE operations."""

    success: bool = Field(description="Whether the operation succeeded.")


class VersionResponse(BaseModel):
    """Response model for version endpoint."""

    api_version: str = Field(description="API version")
    entitybase_version: str = Field(description="EntityBase version")
