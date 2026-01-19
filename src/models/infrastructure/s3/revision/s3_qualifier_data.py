"""S3 qualifier data model."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class S3QualifierData(BaseModel):
    """Model for individual qualifier data stored in S3."""

    model_config = ConfigDict(populate_by_name=True)

    qualifier: dict[str, Any] = Field(
        description="Full qualifier JSON object. Example: {'property': 'P580', 'value': '2023-01-01'}."
    )
    content_hash: int = Field(
        alias="hash", description="Hash of the qualifier content. Example: 123456789."
    )
    created_at: str = Field(
        description="Timestamp when qualifier was created. Example: '2023-01-01T12:00:00Z'."
    )