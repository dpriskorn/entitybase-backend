"""Qualifier and snak response models."""

from typing import Any

from pydantic import BaseModel, Field


class QualifierResponse(BaseModel):
    """Response model for qualifier data."""

    model_config = {"extra": "allow"}  # Allow extra fields from S3 data

    qualifier: dict[str, Any] = Field(
        description="Full qualifier JSON object with reconstructed snaks. Values may be int, str, dict, or list containing reconstructed snaks."
    )
    content_hash: int = Field(
        alias="hash", description="Hash of the qualifier content. Example: 123456789."
    )
    created_at: str = Field(
        description="Timestamp when qualifier was created. Example: '2023-01-01T12:00:00Z'."
    )


class SnakResponse(BaseModel):
    """Response model for snak data."""

    model_config = {"extra": "allow"}  # Allow extra fields from S3 data

    snak: dict[str, Any] = Field(
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
    datavalue: dict[str, Any] | None = Field(
        default=None,
        description="Data value of the snak. Example: {'value': 'Q1', 'type': 'wikibase-entityid'}.",
    )


class SerializableQualifierValue(BaseModel):
    """Serializable form of qualifier values for JSON serialization."""

    model_config = {"extra": "allow"}

    value: dict[str, Any] | int | str | list["SerializableQualifierValue"] | None = (
        Field(
            default=None,
            description="Serializable qualifier value (dict, int, str, or list of SerializableQualifierValue).",
        )
    )
