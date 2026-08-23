from typing import Any

from pydantic import BaseModel, Field


class StatementRecord(BaseModel):
    """Record model for statements table (replaces S3 storage)."""

    content_hash: int
    data: dict[str, Any]
    ref_count: int = Field(default=1)


class QualifierRecord(BaseModel):
    """Record model for qualifiers table (replaces S3 storage)."""

    content_hash: int
    data: dict[str, Any]
    ref_count: int = Field(default=1)


class ReferenceRecord(BaseModel):
    """Record model for refs table (replaces S3 storage)."""

    content_hash: int
    data: dict[str, Any]
    ref_count: int = Field(default=1)


class SnakRecord(BaseModel):
    """Record model for snaks table (replaces S3 storage)."""

    content_hash: int
    data: dict[str, Any]
    ref_count: int = Field(default=1)
