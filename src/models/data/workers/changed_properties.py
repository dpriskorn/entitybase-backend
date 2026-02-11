"""Data models for REST API."""

from pydantic import BaseModel


class ChangedProperties(BaseModel):
    """Model for changed properties in watchlist notifications."""

    properties: list[str] = []
