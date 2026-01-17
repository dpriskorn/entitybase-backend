"""These models are based on the Wikibase data model.
See https://www.mediawiki.org/wiki/Wikibase/DataModel"""

from typing import List

from pydantic import BaseModel, Field


class LabelValue(BaseModel):
    """Individual label entry with language and value."""

    language: str = Field(..., min_length=1)
    value: str = Field(..., min_length=1)


class DescriptionValue(BaseModel):
    """Individual description entry with language and value."""

    language: str = Field(..., min_length=1)
    value: str = Field(..., min_length=1)


class AliasValue(BaseModel):
    """Individual alias entry with language and value."""

    language: str = Field(..., min_length=1)
    value: str = Field(..., min_length=1)


class SitelinkValue(BaseModel):
    """Individual sitelink entry."""

    site: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    url: str = Field(default="")
    badges: List[str] = Field(default_factory=list)
