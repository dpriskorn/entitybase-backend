"""Hash maps for entity labels."""

from pydantic.root_model import RootModel


class LabelsHashes(RootModel[dict[str, int]]):
    """Hash map for entity labels by language."""