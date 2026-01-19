from pydantic import ConfigDict, Field

"""Musical notation value type."""

from typing_extensions import Literal
from .base import Value


class MusicalNotationValue(Value):
    """Value representing musical notation."""

    kind: Literal["musical_notation"] = Field(default="musical_notation", frozen=True)
    value: str
    datatype_uri: str = "http://wikiba.se/ontology#MusicalNotation"

    model_config = ConfigDict(frozen=True)
