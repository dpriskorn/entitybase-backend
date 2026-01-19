"""Hash maps for entity descriptions."""

from pydantic.root_model import RootModel


class DescriptionsHashes(RootModel[dict[str, int]]):
    """Hash map for entity descriptions by language."""
