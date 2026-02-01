"""Response models for lexeme forms and senses endpoints."""

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field


class RepresentationData(BaseModel):
    language: str
    value: str
    model_config = ConfigDict(frozen=True)


class FormResponse(BaseModel):
    id: str
    representations: Dict[str, RepresentationData]
    grammatical_features: List[str] = Field(default_factory=list, alias="grammaticalFeatures")
    claims: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    model_config = ConfigDict(frozen=True)


class SenseResponse(BaseModel):
    id: str
    glosses: Dict[str, RepresentationData]
    claims: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    model_config = ConfigDict(frozen=True)


class FormsResponse(BaseModel):
    forms: List[FormResponse]


class SensesResponse(BaseModel):
    senses: List[SenseResponse]


class FormRepresentationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    value: str


class FormRepresentationsResponse(BaseModel):
    representations: Dict[str, RepresentationData]
    model_config = ConfigDict(extra="forbid")


class SenseGlossesResponse(BaseModel):
    glosses: Dict[str, RepresentationData]
    model_config = ConfigDict(extra="forbid")


class SenseGlossResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    value: str