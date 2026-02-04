"""S3 load response models for typed data retrieval."""

from typing import Any

from pydantic import BaseModel, Field


class StringLoadResponse(BaseModel):
    """Response model for string data from S3."""

    data: str = Field(description="String data from S3")


class DictLoadResponse(BaseModel):
    """Response model for dictionary/JSON data from S3."""

    data: dict[str, Any] = Field(description="Dictionary data from S3")


LoadResponse = StringLoadResponse | DictLoadResponse
