"""Qualifier, reference, and data response models."""

from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field

from models.data.rest_api.v1.entitybase.response.misc import TermsByType, TermsPerLanguage


class QualifierResponse(BaseModel):
    """Response model for qualifier data."""

    model_config = {"extra": "allow"}  # Allow extra fields from S3 data

    qualifier: Dict[str, Any] = Field(
        description="Full qualifier JSON object with reconstructed snaks. Values may be int, str, dict, or list containing reconstructed snaks."
    )
    content_hash: int = Field(
        alias="hash", description="Hash of the qualifier content. Example: 123456789."
    )
    created_at: str = Field(
        description="Timestamp when qualifier was created. Example: '2023-01-01T12:00:00Z'."
    )


class ReferenceResponse(BaseModel):
    """Response model for reference data."""

    model_config = {"extra": "allow"}  # Allow extra fields from S3 data

    reference: Dict[str, Any] = Field(
        description="Full reference JSON object. Example: {'snaks': {'P854': [{'value': 'https://example.com'}]}}."
    )
    content_hash: int = Field(
        alias="hash", description="Hash of the reference content. Example: 123456789."
    )
    created_at: str = Field(
        description="Timestamp when reference was created. Example: '2023-01-01T12:00:00Z'."
    )


class SnakResponse(BaseModel):
    """Response model for snak data."""

    model_config = {"extra": "allow"}  # Allow extra fields from S3 data

    snak: Dict[str, Any] = Field(
        description="Full snak JSON object. Example: {'snaktype': 'value', 'property': 'P31', 'datatype': 'wikibase-item', 'datavalue': {...}}."
    )
    content_hash: int = Field(
        alias="hash", description="Hash of the snak content. Example: 123456789."
    )
    created_at: str = Field(
        description="Timestamp when snak was created. Example: '2023-01-01T12:00:00Z'."
    )


class ReconstructedSnakValue(BaseModel):
    """Response model for reconstructed snak value from hash."""

    model_config = {"extra": "allow"}

    snaktype: str = Field(
        description="Type of snak. Example: 'value', 'novalue', 'somevalue'."
    )
    property: str = Field(description="Property ID. Example: 'P31'.")
    datatype: str | None = Field(
        default=None, description="Datatype of the snak. Example: 'wikibase-item'."
    )
    datavalue: Dict[str, Any] | None = Field(
        default=None,
        description="Data value of the snak. Example: {'value': 'Q1', 'type': 'wikibase-entityid'}."
    )


class SerializableQualifierValue(BaseModel):
    """Serializable form of qualifier values for JSON serialization."""

    model_config = {"extra": "allow"}

    value: Dict[str, Any] | int | str | list["SerializableQualifierValue"] | None = Field(
        default=None,
        description="Serializable qualifier value (dict, int, str, or list of SerializableQualifierValue)."
    )


class GeneralStatsData(BaseModel):
    """Container for computed general wiki statistics."""

    model_config = ConfigDict(populate_by_name=True)

    total_statements: int = Field(description="Total number of statements.")
    total_qualifiers: int = Field(description="Total number of qualifiers.")
    total_references: int = Field(description="Total number of references.")
    total_items: int = Field(description="Total number of items.")
    total_lexemes: int = Field(description="Total number of lexemes.")
    total_properties: int = Field(description="Total number of properties.")
    total_sitelinks: int = Field(description="Total number of sitelinks.")
    total_terms: int = Field(
        description="Total number of terms (labels + descriptions + aliases)."
    )
    terms_per_language: TermsPerLanguage = Field(
        description="Terms count per language."
    )
    terms_by_type: TermsByType = Field(
        description="Terms count by type (labels, descriptions, aliases)."
    )
