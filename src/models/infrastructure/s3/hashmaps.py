from pydantic import RootModel, BaseModel, Field


class LabelsHashes(RootModel[dict[str, int]]):
    """Hash map for entity labels by language."""


class DescriptionsHashes(RootModel[dict[str, int]]):
    """Hash map for entity descriptions by language."""


class AliasesHashes(RootModel[dict[str, list[int]]]):
    """Hash map for entity aliases by language."""


class SitelinksHashes(RootModel[dict[str, int]]):
    """Hash map for entity sitelinks by site."""


class StatementsHashes(RootModel[list[int]]):
    """Hash list for entity statements."""


class HashMaps(BaseModel):
    labels: LabelsHashes | None = Field(default=None)
    descriptions: DescriptionsHashes | None = Field(default=None)
    aliases: AliasesHashes | None = Field(default=None)
    sitelinks: SitelinksHashes | None = Field(default=None)
    statements: StatementsHashes | None = Field(default=None)
