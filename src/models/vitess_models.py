"""Vitess-related models and configurations."""

from pydantic import BaseModel

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
