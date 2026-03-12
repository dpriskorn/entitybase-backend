"""Cleanup operation response models."""

from pydantic import BaseModel, Field


class CleanupOrphanedResponse(BaseModel):
    """Response model for cleanup orphaned statements."""

    cleaned_count: int = Field(
        ...,
        description="Number of statements cleaned up from S3 and Vitess",
    )
    failed_count: int = Field(
        default=0,
        description="Number of statements that failed to clean up",
    )
    errors: list[str] = Field(
        default_factory=list,
        description="List of error messages for failed cleanups",
    )
