"""S3 sitelink data model."""

from typing import List

from pydantic import BaseModel, Field


class S3SitelinkData(BaseModel):
    """Model for individual sitelink data stored in revision."""

    title_hash: int = Field(description="Hash of the sitelink title.")
    badges: List[str] = Field(default_factory=list, description="List of badges associated with the sitelink.")