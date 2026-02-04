from pydantic import ConfigDict, Field, field_validator

from ...rest_api.utils import raise_validation_error

"""Monolingual text value type."""

from typing_extensions import Literal
from .base import Value


class MonolingualValue(Value):
    """Value representing text in a single language."""

    kind: Literal["monolingual"] = Field(default="monolingual", frozen=True)
    value: str
    datatype_uri: str = "http://wikiba.se/ontology#MonolingualText"
    language: str
    text: str

    model_config = ConfigDict(frozen=True)

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        if "\n" in v or "\r" in v:
            raise_validation_error(
                "MonolingualText text must not contain newline characters"
            )
        return v
