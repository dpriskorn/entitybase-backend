from typing import List

from pydantic import BaseModel, Field


class SitelinkData(BaseModel):
    """Data for a single sitelink."""

    title: str = Field(description="Page title")
    badges: List[str] = Field(default=[], description="List of badges")
