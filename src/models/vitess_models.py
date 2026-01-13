"""Vitess-related models and configurations."""

from pydantic import BaseModel, Field

from models.infrastructure.config import Config


class VitessConfig(Config):
    """Configuration for Vitess connections."""

    host: str
    port: int
    database: str
    user: str = "root"
    password: str = ""


class HistoryRecord(BaseModel):
    """Record of entity revision history."""

    revision_id: int
    created_at: str
    is_mass_edit: bool = False


class BacklinkData(BaseModel):
    """Raw backlink data from database."""

    referencing_internal_id: int = Field(
        description="Internal ID of the referencing entity"
    )
    statement_hash: str = Field(description="Hash of the statement")
    property_id: str = Field(description="Property ID")
    rank: str = Field(description="Rank of the statement")
