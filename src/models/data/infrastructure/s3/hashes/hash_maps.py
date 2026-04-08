"""Hash maps model."""

from pydantic import BaseModel, Field

from models.data.infrastructure.s3.hashes.aliases_hashes import AliasesHashes
from models.data.infrastructure.s3.hashes.descriptions_hashes import DescriptionsHashes
from models.data.infrastructure.s3.hashes.labels_hashes import LabelsHashes
from models.data.infrastructure.s3.hashes.sitelinks_hashes import SitelinkHashes
from models.data.infrastructure.s3.hashes.statements_hashes import StatementsHashes


class HashMaps(BaseModel):
    """Container for all entity hash maps."""

    labels: LabelsHashes | None = Field(default=None, description="Label hashes by language")
    descriptions: DescriptionsHashes | None = Field(default=None, description="Description hashes by language")
    aliases: AliasesHashes | None = Field(default=None, description="Alias hashes by language")
    sitelinks: SitelinkHashes | None = Field(default=None, description="Sitelink hashes by site")
    statements: StatementsHashes | None = Field(default=None, description="Statement hashes by property")
