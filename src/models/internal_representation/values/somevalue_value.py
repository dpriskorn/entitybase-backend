from pydantic import ConfigDict, Field
"""Some value type."""

from typing_extensions import Literal
from .base import Value


class SomeValue(Value):
    """Value representing the presence of an unknown value."""

    kind: Literal["somevalue"] = Field(default="somevalue", frozen=True)
    value: None = None
    datatype_uri: str = "http://wikiba.se/ontology#SomeValue"

    model_config = ConfigDict(frozen=True)
