"""Stored statement model."""

from typing import Any

from pydantic import BaseModel, Field


class StatementData(BaseModel):
    """Statement data with reconstructed mainsnak.

    Represents a full statement with typed fields.
    """

    model_config = {"by_alias": True, "extra": "allow"}

    id: str | None = None
    type: str | None = None
    mainsnak: Any = None
    rank: str | None = None
    qualifiers: Any = None
    references: Any = None
    qualifiers_order: list[str] | None = None


class S3Statement(BaseModel):
    """Statement format for S3 storage.

    Compatible with StatementResponse for API responses.
    """

    model_config = {"by_alias": True}

    schema_version: str = Field(alias="schema")
    content_hash: int = Field(alias="hash")
    statement: dict[str, Any]
    created_at: str
