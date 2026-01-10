from pydantic import ConfigDict, Field
"""Commons media value type."""

from typing_extensions import Literal
from .base import Value


class CommonsMediaValue(Value):
    """Value representing a Wikimedia Commons media file."""

    kind: Literal["commons_media"] = Field(default="commons_media", frozen=True)
    value: str
    datatype_uri: str = "http://wikiba.se/ontology#CommonsMedia"

    model_config = ConfigDict(frozen=True)
