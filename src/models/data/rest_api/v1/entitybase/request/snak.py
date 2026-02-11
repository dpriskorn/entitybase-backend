"""Snak request model."""

from typing import Any, Dict

from pydantic import BaseModel


class SnakRequest(BaseModel):
    """Request model for snak input."""

    datavalue: Dict[str, Any]
    property: str
