from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RawEntityData(BaseModel):
    """Model for raw entity JSON data."""

    model_config = ConfigDict(extra="allow")

    data: dict[str, Any] = Field(description="Raw entity data.")
