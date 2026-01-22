from typing import Any

from pydantic import BaseModel, Field


class JsonSchema(BaseModel):
    """Model for JSON schema data."""

    data: dict[str, Any] = Field(..., description="The JSON schema dictionary")
