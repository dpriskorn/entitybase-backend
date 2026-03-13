"""Term response models."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class LabelResponse(BaseModel):
    """Response model for entity labels."""

    value: str = Field(..., description="The label text for the specified language")


class LabelsResponse(BaseModel):
    """Response model for all entity labels."""

    labels: dict[str, str] = Field(..., description="Labels per language")


class DescriptionResponse(BaseModel):
    """Response model for entity descriptions."""

    value: str = Field(
        ..., description="The description text for the specified language"
    )


class DescriptionsResponse(BaseModel):
    """Response model for all entity descriptions."""

    descriptions: dict[str, str] = Field(..., description="Descriptions per language")


class AliasesResponse(BaseModel):
    """Response model for entity aliases."""

    aliases: list[str] = Field(
        ..., description="List of alias texts for the specified language"
    )


class BatchLabelsResponse(BaseModel):
    """Response model for batch labels lookup by hash."""

    labels: dict[str, str] = Field(
        default_factory=dict,
        description="Dictionary mapping hash strings to label text",
    )


class BatchDescriptionsResponse(BaseModel):
    """Response model for batch descriptions lookup by hash."""

    descriptions: dict[str, str] = Field(
        default_factory=dict,
        description="Dictionary mapping hash strings to description text",
    )


class BatchAliasesResponse(BaseModel):
    """Response model for batch aliases lookup by hash."""

    aliases: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Dictionary mapping hash strings to alias text lists",
    )


class TermsResponse(BaseModel):
    """Model for batch terms result."""

    terms: dict[int, tuple[str, str]] = Field(..., description="Terms by hash")


class TermsPerLanguage(BaseModel):
    """Model for terms count per language."""

    model_config = ConfigDict(extra="allow")

    terms: dict[str, int] = Field(description="Language to count mapping.")


class TermsByType(BaseModel):
    """Model for terms count by type."""

    model_config = ConfigDict(extra="allow")

    counts: dict[str, int] = Field(description="Type to count mapping.")


class TermHashResponse(BaseModel):
    """Response for single term (label/description/alias/lemma) operations."""

    hash: int = Field(description="Hash of the stored term.")


class TermHashesResponse(BaseModel):
    """Response for multi-term operations (e.g., aliases PUT)."""

    hashes: list[int] = Field(description="Hashes of the stored terms.")
