"""Response models for thanks operations."""

from typing import List

from pydantic import BaseModel

from models.thanks import ThankItem


class ThankResponse(BaseModel):
    """Response for sending a thank."""

    thank_id: int
    from_user_id: int
    to_user_id: int
    entity_id: str
    revision_id: int
    created_at: str  # ISO format datetime string


class ThanksListResponse(BaseModel):
    """Response for thanks list queries."""

    user_id: int
    thanks: List[ThankItem]
    total_count: int
    has_more: bool
