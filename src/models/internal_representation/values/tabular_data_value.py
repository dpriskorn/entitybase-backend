from pydantic import ConfigDict, Field

"""Tabular data value type."""

from typing_extensions import Literal
from .handler import Value


class TabularDataValue(Value):
    """Value representing tabular data."""

    kind: Literal["tabular_data"] = Field(default="tabular_data", frozen=True)
    value: str
    datatype_uri: str = "http://wikiba.se/ontology#TabularData"

    model_config = ConfigDict(frozen=True)
