from pydantic import ConfigDict, Field

"""No value type."""

from typing_extensions import Literal
from .base import Value


class NoValue(Value):
    """Value representing the absence of a value."""

    kind: Literal["novalue"] = Field(default="novalue", frozen=True)
    value: None = None
    datatype_uri: str = "http://wikiba.se/ontology#NoValue"

    model_config = ConfigDict(frozen=True)
