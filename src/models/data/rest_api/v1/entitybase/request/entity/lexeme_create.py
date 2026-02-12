"""Request models for lexeme form and sense creation."""

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field


class FormCreateRequest(BaseModel):
    """Request body for creating a new form."""

    model_config = ConfigDict(extra="forbid")

    representations: Dict[str, Dict[str, str]] = Field(
        ...,
        description="Form representations by language code, e.g. {'en': {'language': 'en', 'value': 'runs'}}",
    )
    grammatical_features: List[str] = Field(
        default_factory=list,
        description="List of grammatical feature item IDs (e.g. ['Q123'])",
    )
    claims: Dict[str, List[Dict[str, Any]]] = Field(
        default_factory=dict,
        description="Optional statements/claims for the form",
    )


class SenseCreateRequest(BaseModel):
    """Request body for creating a new sense."""

    model_config = ConfigDict(extra="forbid")

    glosses: Dict[str, Dict[str, str]] = Field(
        ...,
        description="Sense glosses by language code, e.g. {'en': {'language': 'en', 'value': 'to move quickly'}}",
    )
    claims: Dict[str, List[Dict[str, Any]]] = Field(
        default_factory=dict,
        description="Optional statements/claims for the sense",
    )
