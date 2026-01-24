"""Miscellaneous request models."""

from pydantic import BaseModel, Field


class CleanupOrphanedRequest(BaseModel):
    older_than_days: int = Field(
        default=180,
        ge=1,
        le=365,
        description="Minimum age in days before cleanup (default 180)",
    )
    limit: int = Field(
        default=1000,
        ge=1,
        le=10000,
        description="Maximum number of statements to cleanup (default 1000)",
    )
