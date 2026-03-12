"""Sitelink response models."""

from typing import Any

from pydantic import BaseModel, Field


class AllSitelinksResponse(BaseModel):
    """Response model for all entity sitelinks."""

    sitelinks: dict[str, Any] = Field(
        ..., description="Dictionary mapping site key to sitelink data"
    )


class SitelinksResponse(BaseModel):
    """Response model for all entity sitelinks."""

    sitelinks: dict[str, str] = Field(..., description="Sitelinks per site")


class BatchSitelinksResponse(BaseModel):
    """Response model for batch sitelinks lookup by hash."""

    sitelinks: dict[str, str] = Field(
        default_factory=dict,
        description="Dictionary mapping hash strings to sitelink titles",
    )
