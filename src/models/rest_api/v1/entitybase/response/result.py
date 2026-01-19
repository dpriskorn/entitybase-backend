"""Result response models."""

from pydantic import BaseModel, Field


class RevisionIdResult(BaseModel):
    """Model for operations that return a revision ID."""

    revision_id: int = Field(
        default=0,
        description="The revision ID of the created/updated entity, or 0 for idempotent operations",
    )


class RevisionResult(BaseModel):
    """Result of revision processing."""

    success: bool = Field(description="Whether the revision processing was successful")
    revision_id: int = Field(
        default=0, description="The ID of the created or updated revision"
    )
    error: str = Field(default="", description="Error message if the operation failed")
