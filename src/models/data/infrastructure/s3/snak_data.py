"""S3 snak data model."""

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
