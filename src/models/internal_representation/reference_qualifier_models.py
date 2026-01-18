"""Models for reference and qualifier data structures."""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class ReferenceModel(BaseModel):
    """Model for reference data structure."""

    hash: str = Field(..., description="Hash of the reference")
    snaks: Dict[str, List[Dict[str, Any]]] = Field(
        ..., description="Snaks grouped by property"
    )
    snaks_order: List[str] = Field(..., description="Order of properties in snaks")


class QualifierModel(BaseModel):
    """Model for qualifier data structure."""

    qualifiers: Dict[str, List[Dict[str, Any]]] = Field(
        ..., description="Qualifiers grouped by property"
    )
