"""ID response model for entity ID generation."""

from pydantic import BaseModel, Field


class IdResponse(BaseModel):
    """Response model for generated entity ID."""

    id: str = Field(..., description="The generated entity ID (e.g., 'Q123', 'P456')")