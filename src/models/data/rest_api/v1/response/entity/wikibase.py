"""These models are based on the Wikibase data model.
See https://www.mediawiki.org/wiki/Wikibase/DataModel"""

from typing import List

from pydantic import BaseModel, Field


class LabelValue(BaseModel):
    """Individual label entry with language and value."""

    language: str = Field(
        ..., min_length=1, description="Language code for the label. Example: 'en'."
    )
    value: str = Field(
        ..., min_length=1, description="The label text. Example: 'Test Label'."
    )


class DescriptionValue(BaseModel):
    """Individual description entry with language and value."""

    language: str = Field(
        ...,
        min_length=1,
        description="Language code for the description. Example: 'en'.",
    )
    value: str = Field(
        ...,
        min_length=1,
        description="The description text. Example: 'A test description'.",
    )


class AliasValue(BaseModel):
    """Individual alias entry with language and value."""

    language: str = Field(
        ..., min_length=1, description="Language code for the alias. Example: 'en'."
    )
    value: str = Field(
        ..., min_length=1, description="The alias text. Example: 'Alternative Name'."
    )


class SitelinkValue(BaseModel):
    """Individual sitelink entry."""

    site: str = Field(
        ...,
        min_length=1,
        description="Site identifier for the sitelink. Example: 'enwiki'.",
    )
    title: str = Field(
        ..., min_length=1, description="Page title on the site. Example: 'Test Page'."
    )
    url: str = Field(
        default="",
        description="URL of the page. Example: 'https://en.wikipedia.org/wiki/Test_Page'.",
    )
    badges: List[str] = Field(
        default_factory=list,
        description="List of badges associated with the sitelink. Example: ['featuredarticle']",
    )
