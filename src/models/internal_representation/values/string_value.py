from pydantic import ConfigDict, Field

"""String value type."""

from typing_extensions import Literal
from .base import Value


class StringValue(Value):
    """Value representing a string datatype."""

    kind: Literal["string"] = Field(default="string", frozen=True)
    value: str
    datatype_uri: str = "http://wikiba.se/ontology#String"

    model_config = ConfigDict(frozen=True)
