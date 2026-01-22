"""Hash maps model."""

from pydantic import BaseModel, Field

from models.data.infrastructure.s3.hashes.aliases_hashes import AliasesHashes
from models.data.infrastructure.s3.hashes.descriptions_hashes import DescriptionsHashes
from models.data.infrastructure.s3.hashes.labels_hashes import LabelsHashes
from models.data.infrastructure.s3.hashes.sitelinks_hashes import SitelinksHashes
from models.data.infrastructure.s3.hashes.statements_hashes import StatementsHashes


class HashMaps(BaseModel):
    labels: LabelsHashes | None = Field(default=None)
    descriptions: DescriptionsHashes | None = Field(default=None)
    aliases: AliasesHashes | None = Field(default=None)
    sitelinks: SitelinksHashes | None = Field(default=None)
    statements: StatementsHashes | None = Field(default=None)
