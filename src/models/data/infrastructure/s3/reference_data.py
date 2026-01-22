"""S3 reference data model."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class S3ReferenceData(BaseModel):
    """Model for individual reference data stored in S3."""

    model_config = ConfigDict(populate_by_name=True)

    reference: dict[str, Any] = Field(
        description="Full reference JSON object. Example: {'snaks': {'P854': [{'value': 'https://example.com'}]}}."
    )
    content_hash: int = Field(
        alias="hash", description="Hash of the reference content. Example: 123456789."
    )
    created_at: str = Field(
        description="Timestamp when reference was created. Example: '2023-01-01T12:00:00Z'."
    )
