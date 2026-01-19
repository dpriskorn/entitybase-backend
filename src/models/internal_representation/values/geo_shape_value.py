from pydantic import ConfigDict, Field

"""Geographic shape value type."""

from typing_extensions import Literal
from .handler import Value


class GeoShapeValue(Value):
    """Value representing a geographic shape."""

    kind: Literal["geo_shape"] = Field(default="geo_shape", frozen=True)
    value: str
    datatype_uri: str = "http://wikiba.se/ontology#GeoShape"

    model_config = ConfigDict(frozen=True)
