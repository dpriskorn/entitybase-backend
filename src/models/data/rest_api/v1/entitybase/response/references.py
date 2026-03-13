"""Reference response models."""

from typing import Any

from pydantic import BaseModel, Field


class ReferenceResponse(BaseModel):
    """Response model for reference data."""

    model_config = {"extra": "allow"}  # Allow extra fields from S3 data

    reference: dict[str, Any] = Field(
        description="Full reference JSON object. Example: {'snaks': {'P854': [{'value': 'https://example.com'}]}}."
    )
    content_hash: int = Field(
        alias="hash", description="Hash of the reference content. Example: 123456789."
    )
    created_at: str = Field(
        description="Timestamp when reference was created. Example: '2023-01-01T12:00:00Z'."
    )


class ReferenceSnaks(BaseModel):
    """Model for reference snaks structure (inner reference data)."""

    model_config = {"extra": "allow"}

    snaks: dict[str, Any]
    snaks_order: list[str] | None = None
