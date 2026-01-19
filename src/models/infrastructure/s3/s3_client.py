"""S3 storage client for entity and statement data."""

import logging
from typing import Any, Dict, Optional, TYPE_CHECKING

from boto3.session import Session as BotoSession  # noqa  # type: ignore[import-untyped]
from botocore.exceptions import ClientError  # type: ignore[import-untyped]
from pydantic import Field

from models.common import OperationResult
from models.infrastructure.client import Client
from models.infrastructure.s3.config import S3Config
from models.infrastructure.s3.connection import S3ConnectionManager
from models.infrastructure.s3.revision.revision_data import RevisionData
from models.infrastructure.s3.revision.revision_read_response import RevisionReadResponse
from models.infrastructure.s3.revision.s3_qualifier_data import S3QualifierData
from models.infrastructure.s3.revision.s3_reference_data import S3ReferenceData
from models.infrastructure.s3.storage.metadata_storage import MetadataStorage
from models.infrastructure.s3.storage.qualifier_storage import QualifierStorage
from models.infrastructure.s3.storage.reference_storage import ReferenceStorage
from models.infrastructure.s3.storage.revision_storage import RevisionStorage
from models.infrastructure.s3.storage.statement_storage import StatementStorage
from models.rest_api.entitybase.response import StatementResponse
from models.rest_api.utils import raise_validation_error

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class MyS3Client(Client):
    """Client for S3 storage operations."""

    config: S3Config  # type: ignore[override]
    connection_manager: Optional[S3ConnectionManager] = Field(
        default=None, exclude=True
    )  # type: ignore[override]
    revisions: Optional[RevisionStorage] = Field(default=None, exclude=True)
    statements: Optional[StatementStorage] = Field(default=None, exclude=True)
    metadata: Optional[MetadataStorage] = Field(default=None, exclude=True)
    references: Optional[ReferenceStorage] = Field(default=None, exclude=True)
    qualifiers: Optional[QualifierStorage] = Field(default=None, exclude=True)

    def __init__(self, config: S3Config, **kwargs: Any) -> None:
        super().__init__(config=config, **kwargs)
        manager = S3ConnectionManager(config=config)
        if manager is None:
            raise_validation_error("S3 service unavailable", status_code=503)
        self.connection_manager = manager  # type: ignore[assignment]
        self.connection_manager.connect()
        # self._ensure_bucket_exists()

        # Initialize storage components
        self.revisions = RevisionStorage(self.connection_manager)
        self.statements = StatementStorage(self.connection_manager)
        self.metadata = MetadataStorage(self.connection_manager)
        self.references = ReferenceStorage(self.connection_manager)
        self.qualifiers = QualifierStorage(self.connection_manager)

    def write_revision(
        self,
        entity_id: str,
        revision_id: int,
        data: RevisionData,
    ) -> OperationResult[None]:
        """Write entity revision data to S3."""
        return self.revisions.store_revision(entity_id, revision_id, data)

    def read_revision(self, entity_id: str, revision_id: int) -> RevisionReadResponse:
        """Read S3 object and return parsed JSON."""
        return self.revisions.load_revision(entity_id, revision_id)

    def mark_published(
        self, entity_id: str, revision_id: int, publication_state: str
    ) -> None:
        """Update the publication state of an entity revision."""
        self.revisions.mark_published(entity_id, revision_id, publication_state)

    def delete_statement(self, content_hash: int) -> None:
        """Delete statement from S3."""
        result = self.statements.delete_statement(content_hash)
        if not result.success:
            raise_validation_error("S3 storage service unavailable", status_code=503)

    def write_statement(
        self,
        content_hash: int,
        statement_data: Dict[str, Any],
        schema_version: str,
    ) -> None:
        """Write statement snapshot to S3."""
        result = self.statements.store_statement(content_hash, statement_data, schema_version)
        if not result.success:
            raise_validation_error("S3 storage service unavailable", status_code=503)

    def read_statement(self, content_hash: int) -> "StatementResponse":
        """Read statement snapshot from S3."""
        return self.statements.load_statement(content_hash)

    def delete_metadata(self, metadata_type: str, content_hash: int) -> None:
        """Delete metadata content from S3 when ref_count reaches 0."""
        result = self.metadata.delete_metadata(metadata_type, content_hash)
        if not result.success:
            logger.error(f"S3 delete_metadata failed for {metadata_type}:{content_hash}")

    def store_term_metadata(self, term: str, content_hash: int) -> None:
        """Store term metadata as plain UTF-8 text in S3."""
        # Assume term type is "labels" for now, but could be generalized
        # Since old method didn't specify type, use "labels" as default
        result = self.metadata.store_metadata("labels", content_hash, term)
        if not result.success:
            raise_validation_error("S3 storage service unavailable", status_code=503)

    def load_term_metadata(self, content_hash: int) -> str:
        """Load term metadata as plain UTF-8 text from S3."""
        return self.metadata.load_metadata("labels", content_hash)

    def store_sitelink_metadata(self, title: str, content_hash: int) -> None:
        """Store sitelink metadata as plain UTF-8 text in S3."""
        result = self.metadata.store_metadata("sitelinks", content_hash, title)
        if not result.success:
            raise_validation_error("S3 storage service unavailable", status_code=503)

    def load_sitelink_metadata(self, content_hash: int) -> str:
        """Load sitelink metadata as plain UTF-8 text from S3."""
        return self.metadata.load_metadata("sitelinks", content_hash)

    def load_metadata(self, metadata_type: str, content_hash: int) -> str:
        """Load metadata by type."""
        return self.metadata.load_metadata(metadata_type, content_hash)

    def store_reference(self, content_hash: int, reference_data: S3ReferenceData) -> None:
        """Store a reference by its content hash."""
        result = self.references.store_reference(content_hash, reference_data)
        if not result.success:
            raise_validation_error("S3 storage service unavailable", status_code=503)

    def load_reference(self, content_hash: int) -> S3ReferenceData:
        """Load a reference by its content hash."""
        return self.references.load_reference(content_hash)

    def load_references_batch(self, content_hashes: list[int]) -> list[S3ReferenceData | None]:
        """Load multiple references by their content hashes."""
        return self.references.load_references_batch(content_hashes)

    def store_qualifier(self, content_hash: int, qualifier_data: S3QualifierData) -> None:
        """Store a qualifier by its content hash."""
        result = self.qualifiers.store_qualifier(content_hash, qualifier_data)
        if not result.success:
            raise_validation_error("S3 storage service unavailable", status_code=503)

    def load_qualifier(self, content_hash: int) -> S3QualifierData:
        """Load a qualifier by its content hash."""
        return self.qualifiers.load_qualifier(content_hash)

    def load_qualifiers_batch(self, content_hashes: list[int]) -> list[S3QualifierData | None]:
        """Load multiple qualifiers by their content hashes."""
        return self.qualifiers.load_qualifiers_batch(content_hashes)


# MyS3Client.model_rebuild()
