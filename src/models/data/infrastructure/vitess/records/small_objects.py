from typing import Any

from pydantic import BaseModel, Field


class StatementRecord(BaseModel):
    """Record model for statements table (replaces S3 storage)."""

    content_hash: int = Field(..., description="Hash of the statement content")
    data: dict[str, Any] = Field(..., description="Statement data dictionary")
    ref_count: int = Field(default=1, description="Reference count for caching")


class QualifierRecord(BaseModel):
    """Record model for qualifiers table (replaces S3 storage)."""

    content_hash: int = Field(..., description="Hash of the qualifier content")
    data: dict[str, Any] = Field(..., description="Qualifier data dictionary")
    ref_count: int = Field(default=1, description="Reference count for caching")


class ReferenceRecord(BaseModel):
    """Record model for refs table (replaces S3 storage)."""

    content_hash: int = Field(..., description="Hash of the reference content")
    data: dict[str, Any] = Field(..., description="Reference data dictionary")
    ref_count: int = Field(default=1, description="Reference count for caching")


class SnakRecord(BaseModel):
    """Record model for snaks table (replaces S3 storage)."""

    content_hash: int = Field(..., description="Hash of the snak content")
    data: dict[str, Any] = Field(..., description="Snak data dictionary")
    ref_count: int = Field(default=1, description="Reference count for caching")
