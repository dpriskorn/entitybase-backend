import re

from pydantic import ConfigDict, Field, field_validator
from typing_extensions import Literal
from ...validation.utils import raise_validation_error
from .base import Value


class TimeValue(Value):
    kind: Literal["time"] = Field(default="time", frozen=True)
    value: str
    datatype_uri: str = "http://wikiba.se/ontology#Time"
    timezone: int = 0
    before: int = 0
    after: int = 0
    precision: int = Field(ge=0, le=14)
    calendarmodel: str = "http://www.wikidata.org/entity/Q1985727"

    model_config = ConfigDict(frozen=True)

    @field_validator("value")
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        if not (v.startswith("+") or v.startswith("-")):
            v = "+" + v

        pattern = re.compile(
            r"^[+-][0-9]{1,16}-(?:1[0-2]|0[0-9])-(?:3[01]|0[0-9]|[12][0-9])T(?:2[0-3]|[01][0-9]):[0-5][0-9]:[0-5][0-9]Z$"
        )
        if not pattern.match(v):
            raise_validation_error(
                f"Time value must be in format '+%Y-%m-%dT%H:%M:%SZ', got: {v}",
                status_code=500,
            )
        return v

    @field_validator("calendarmodel")
    @classmethod
    def validate_calendarmodel(cls, v: str) -> str:
        if not v.startswith("http://www.wikidata.org/entity/Q"):
            if v.startswith("Q"):
                v = "http://www.wikidata.org/entity/" + v
            else:
                raise_validation_error(
                    f"Calendar model must be a Wikidata entity URI or QID, got: {v}"
                )
        return v
