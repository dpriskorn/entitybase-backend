"""Property counts model."""

from pydantic.root_model import RootModel


class PropertyCounts(RootModel[dict[str, int]]):
    """Model for property statement counts (dictionary mapping property ID to statement count)."""
