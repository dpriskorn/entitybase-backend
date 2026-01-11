from pydantic import ConfigDict, Field
"""URL value type."""

from typing_extensions import Literal
from .base import Value


class URLValue(Value):
    """Value representing a URL."""

    kind: Literal["url"] = Field(default="url", frozen=True)
    value: str
    datatype_uri: str = "http://wikiba.se/ontology#Url"

    model_config = ConfigDict(frozen=True)
