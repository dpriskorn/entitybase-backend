"""Meilisearch data models."""

from pydantic import BaseModel, ConfigDict, Field
from typing import Any


class FlattenedClaims(BaseModel):
    """Model for flattened claims mapping property_id to list of values."""

    model_config = ConfigDict(populate_by_name=True)

    data: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Flat claims dict: property_id -> list of value IDs/values",
    )


class MeilisearchDocument(BaseModel):
    """Model for Meilisearch document from Wikibase entity."""

    model_config = ConfigDict(populate_by_name=True)

    entity_id: str = Field(
        alias="@id", description="Entity ID (Q-number, P-number, L-number, etc.)"
    )
    entity_type: str = Field(
        alias="@type", description="Entity type (item, property, lexeme, etc.)"
    )
    lastrevid: int = Field(description="Last revision ID")
    modified: str = Field(description="Last modified timestamp")
    datatype: str | None = Field(default=None, description="Datatype for properties")
    labels: dict[str, Any] = Field(
        default_factory=dict, description="Entity labels by language"
    )
    descriptions: dict[str, Any] = Field(
        default_factory=dict, description="Entity descriptions by language"
    )
    aliases: dict[str, Any] = Field(
        default_factory=dict, description="Entity aliases by language"
    )
    claims: dict[str, Any] = Field(
        default_factory=dict, description="Entity claims/statements"
    )
    claims_flat: FlattenedClaims = Field(
        default_factory=FlattenedClaims,
        description="Flattened claims for easier querying",
    )
    lemmas: dict[str, Any] | None = Field(
        default=None, description="Lexeme lemmas (for lexeme entities)"
    )
    forms: list[Any] | None = Field(
        default=None, description="Lexeme forms (for lexeme entities)"
    )
    senses: list[Any] | None = Field(
        default=None, description="Lexeme senses (for lexeme entities)"
    )
    language: str | None = Field(
        default=None, description="Lexeme language (for lexeme entities)"
    )
    lexicalCategory: str | None = Field(
        default=None, description="Lexeme lexical category (for lexeme entities)"
    )


class MeilisearchDocumentResponse(BaseModel):
    """Response model for Meilisearch document retrieval."""

    model_config = ConfigDict(populate_by_name=True)

    data: MeilisearchDocument | None = Field(
        default=None, description="The document data if found"
    )