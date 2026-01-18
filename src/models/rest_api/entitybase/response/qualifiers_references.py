"""Qualifier and reference response models."""

from typing import Any, Dict

from pydantic import BaseModel, Field


class QualifierResponse(BaseModel):
    """Response model for qualifier data."""

    model_config = {"extra": "allow"}  # Allow extra fields from S3 data

    qualifier: Dict[str, Any] = Field(
        description="Full qualifier JSON object. Example: {'property': 'P580', 'value': '2023-01-01'}."
    )
    content_hash: int = Field(
        alias="hash", description="Hash of the qualifier content. Example: 123456789."
    )
    qualifier: Dict[str, Any] = Field(
        description="Full qualifier JSON object. Example: {'property': 'P580', 'value': '2023-01-01'}."
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
    reference: Dict[str, Any] = Field(
        description="Full reference JSON object. Example: {'snaks': {'P854': [{'value': 'https://example.com'}]}}."
    )
    created_at: str = Field(
        description="Timestamp when reference was created. Example: '2023-01-01T12:00:00Z'."
    )
