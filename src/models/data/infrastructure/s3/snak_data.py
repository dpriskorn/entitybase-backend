"""S3 snak data models."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class S3SnakData(BaseModel):
    """Model for individual snak data stored in S3."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    schema_version: str = Field(
        alias="schema",
        description="Schema version (MAJOR.MINOR.PATCH). Example: '1.0.0'.",
    )
    snak: dict[str, Any] = Field(
        description="Full snak JSON object. Example: {'snaktype': 'value', 'property': 'P31', 'datatype': 'wikibase-item', 'datavalue': {...}}."
    )
    content_hash: int = Field(
        alias="hash", description="Hash of the snak content. Example: 123456789."
    )
    created_at: str = Field(
        description="Timestamp when snak was created. Example: '2023-01-01T12:00:00Z'."
    )


class ProcessedSnakValue(BaseModel):
    """Represents a processed snak value that can be either a hash or original value."""

    model_config = ConfigDict(populate_by_name=True)

    value: int | str | dict[str, Any] | list[Any] | float | None = Field(
        description="Processed snak value - can be hash, string, dict, list, float, or None."
    )


class ProcessedSnakList(BaseModel):
    """Return type for _process_snak_list_value."""

    model_config = ConfigDict(populate_by_name=True)

    key: str = Field(description="Property key for the snak list.")
    values: list[ProcessedSnakValue] = Field(
        description="List of processed snak values."
    )


class S3ReferenceSnaks(BaseModel):
    """Model for processed reference data with snaks.

    Used as return type for _process_reference_snaks function.
    Contains the processed reference data with hash-referenced snaks.
    """

    model_config = ConfigDict(populate_by_name=True)

    snaks: dict[str, Any] = Field(
        description="Processed snaks dict with property keys."
    )
    snaks_order: list[Any] = Field(
        default_factory=list,
        description="Order of snak properties."
    )
