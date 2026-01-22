"""Hash maps for entity aliases."""

from pydantic.root_model import RootModel


class AliasesHashes(RootModel[dict[str, list[int]]]):
    """Hash map for entity aliases by language."""
