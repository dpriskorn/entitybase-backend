"""Thanks models."""

from datetime import datetime

from pydantic import BaseModel


class ThankItem(BaseModel):
    """Thank record."""

    id: int
    from_user_id: int
    to_user_id: int
    entity_id: str
    revision_id: int
    created_at: datetime


class Thank(BaseModel):
    """Thank record."""

    id: int
    from_user_id: int
    to_user_id: int
    entity_id: str
    revision_id: int
    created_at: datetime
