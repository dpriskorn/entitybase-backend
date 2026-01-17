from pydantic import ConfigDict, Field, field_validator, model_validator

"""Quantity value type."""

from typing_extensions import Literal
from typing import Optional
from ...validation.utils import raise_validation_error
from .base import Value


class QuantityValue(Value):
    """Value representing a quantity with optional bounds."""

    kind: Literal["quantity"] = Field(default="quantity", frozen=True)
    value: str
    datatype_uri: str = "http://wikiba.se/ontology#Quantity"
    unit: str = "1"
    upper_bound: str = Field(default="")
    lower_bound: str = Field(default="")

    model_config = ConfigDict(frozen=True)

    @field_validator("unit")
    @classmethod
    def validate_unit(cls, v: str) -> str:
        """Validate and normalize unit URIs."""
        if v.startswith("Q"):
            v = "http://www.wikidata.org/entity/" + v
        return v

    @field_validator("value", "upper_bound", "lower_bound")
    @classmethod
    def validate_numeric(cls, v: str) -> str:
        """Validate that numeric fields contain valid numbers."""
        if v:
            try:
                float(v)
            except ValueError:
                raise_validation_error(
                    f"Value must be a valid number, got: {v}", status_code=500
                )
        return v

    @model_validator(mode="after")
    def validate_bounds(self) -> "QuantityValue":
        """Validate that bounds are logically consistent."""
        amount = float(self.value)
        upper = float(self.upper_bound) if self.upper_bound else None
        lower = float(self.lower_bound) if self.lower_bound else None

        if lower is not None and upper is not None:
            if lower > upper:
                raise_validation_error(
                    "Lower bound cannot be greater than upper bound", status_code=500
                )
            if lower > amount:
                raise_validation_error(
                    "Lower bound cannot be greater than amount", status_code=500
                )
        if upper is not None and upper < amount:
            raise_validation_error(
                "Upper bound cannot be less than amount", status_code=500
            )
        return self
