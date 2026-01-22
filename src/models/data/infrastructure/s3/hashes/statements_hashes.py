"""Statements hashes model."""

from pydantic import BaseModel, Field


class StatementsHashes(BaseModel):
    """Hash structure for entity statements."""

    root: list[int] = Field(description="List of statement hashes.")
