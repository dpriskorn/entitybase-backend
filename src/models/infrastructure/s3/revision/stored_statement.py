"""Stored statement model."""

from typing import Any

from pydantic import BaseModel, Field


class StoredStatement(BaseModel):
    """Statement format for S3 storage.

    Compatible with StatementResponse for API responses.
    """

    model_config = {"by_alias": True}

    schema_version: str = Field(alias="schema")
    content_hash: int = Field(alias="hash")
    statement: dict[str, Any]
    created_at: str