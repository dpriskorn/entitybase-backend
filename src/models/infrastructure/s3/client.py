"""S3 storage client for entity and statement data."""

import logging
from typing import TYPE_CHECKING, Any, List, Optional, cast

from boto3.session import Session as BotoSession  # noqa  # type: ignore[import-untyped]
from botocore.exceptions import ClientError  # type: ignore[import-untyped]
from pydantic import Field

from models.data.infrastructure.s3 import (
    DictLoadResponse,
    LoadResponse,
    StringLoadResponse,
    S3RevisionData,
)

if TYPE_CHECKING:
    pass

from models.data.common import OperationResult
from models.data.infrastructure.s3.enums import MetadataType
from models.data.infrastructure.s3.qualifier_data import S3QualifierData
from models.data.infrastructure.s3.reference_data import S3ReferenceData
from models.data.infrastructure.s3.snak_data import S3SnakData
from models.infrastructure.client import Client
from models.infrastructure.s3.connection import S3ConnectionManager
from models.infrastructure.s3.revision.revision_data import RevisionData
from models.infrastructure.s3.storage.revision_storage import RevisionStorage
from models.infrastructure.vitess.repositories.revision import RevisionRepository
from models.infrastructure.vitess.storage.qualifier_storage import (
    QualifierVitessStorage,
)
from models.infrastructure.vitess.storage.reference_storage import (
    ReferenceVitessStorage,
)
from models.infrastructure.vitess.storage.snak_storage import SnakVitessStorage
from models.infrastructure.vitess.storage.statement_storage import (
    StatementVitessStorage,
)
from models.infrastructure.vitess.storage.metadata_storage import (
    MetadataVitessStorage,
    SitelinkVitessStorage,
)
from models.data.rest_api.v1.entitybase.response import StatementResponse
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)


class MyS3Client(Client):
    """Client for S3 storage operations."""

    vitess_client: Optional[Any] = Field(default=None, exclude=True)
    vitess_statements: Any = Field(default=None, exclude=True)
    vitess_qualifiers: Any = Field(default=None, exclude=True)
    vitess_references: Any = Field(default=None, exclude=True)
    vitess_snaks: Any = Field(default=None, exclude=True)
    vitess_metadata: Any = Field(default=None, exclude=True)
    vitess_sitelinks: Any = Field(default=None, exclude=True)
    connection_manager: Optional[S3ConnectionManager] = Field(
        default=None, exclude=True
    )  # type: ignore[override]
    revisions: Any = Field(default=None, exclude=True)

    def model_post_init(self, context: Any) -> None:
        # noinspection PyTypeChecker
        manager = S3ConnectionManager(config=self.config)
        if manager is None:
            raise_validation_error("S3 service unavailable", status_code=503)
        self.connection_manager = manager  # type: ignore[assignment]
        self.connection_manager.connect()
        # self._ensure_bucket_exists()

        # Initialize S3 storage components (revisions only now, metadata moved to Vitess)
        from models.infrastructure.s3.storage.revision_storage import RevisionStorage

        self.revisions = RevisionStorage(connection_manager=self.connection_manager)

        # Initialize Vitess storage components (statements, qualifiers, refs, snaks, metadata)
        if self.vitess_client is not None:
            self.vitess_statements = StatementVitessStorage(
                vitess_client=self.vitess_client
            )
            self.vitess_qualifiers = QualifierVitessStorage(
                vitess_client=self.vitess_client
            )
            self.vitess_references = ReferenceVitessStorage(
                vitess_client=self.vitess_client
            )
            self.vitess_snaks = SnakVitessStorage(vitess_client=self.vitess_client)
            self.vitess_metadata = MetadataVitessStorage(
                vitess_client=self.vitess_client
            )
            self.vitess_sitelinks = SitelinkVitessStorage(
                vitess_client=self.vitess_client
            )

    def write_revision(
        self,
        data: RevisionData,
    ) -> OperationResult[None]:
        """Write entity revision data to S3."""
        import json
        from models.internal_representation.metadata_extractor import MetadataExtractor
        from models.data.infrastructure.s3.revision_data import S3RevisionData

        revision_dict = data.model_dump(mode="json")
        revision_json = json.dumps(revision_dict, sort_keys=True)
        content_hash = MetadataExtractor.hash_string(revision_json)

        s3_revision_data = S3RevisionData(
            schema=data.schema_version,
            revision=revision_dict,
            hash=content_hash,
            created_at=data.created_at,
        )

        return self.revisions.store_revision(content_hash, s3_revision_data)  # type: ignore[no-any-return]

    def read_revision(self, entity_id: str, revision_id: int) -> S3RevisionData:
        """Read S3 object and return parsed JSON."""
        if self.vitess_client is None:
            raise_validation_error("Vitess client not configured", status_code=503)
        vitess_client = cast(Any, self.vitess_client)
        internal_id = vitess_client.id_resolver.resolve_id(entity_id)
        if not internal_id:
            raise_validation_error("Entity not found", status_code=404)

        revision_repo = RevisionRepository(vitess_client=self.vitess_client)
        content_hash = revision_repo.get_content_hash(internal_id, revision_id)
        if content_hash == 0:
            raise_validation_error("Revision not found", status_code=404)

        return cast(S3RevisionData, self.revisions.load_revision(content_hash))

    read_full_revision = read_revision
    write_entity_revision = write_revision

    def delete_statement(self, content_hash: int) -> None:
        """Delete statement from Vitess storage."""
        if not hasattr(self, "vitess_statements") or not self.vitess_statements:
            raise_validation_error("Vitess storage not configured", status_code=503)
        result = self.vitess_statements.delete_statement(content_hash)
        if not result.success:
            raise_validation_error("Storage service unavailable", status_code=503)

    def write_statement(
        self,
        content_hash: int,
        statement_data: dict[str, Any],
        schema_version: str,
    ) -> None:
        """Write statement snapshot to Vitess."""
        logger.debug(
            f"[CLIENT_WRITE_STMT] content_hash={content_hash}, "
            f"schema_version={schema_version}, data_keys={list(statement_data.keys())}"
        )
        stmt_data = {
            "statement": statement_data.get("statement", statement_data),
            "schema": schema_version,
            "hash": content_hash,
            "created_at": statement_data.get("created_at", ""),
        }
        if not hasattr(self, "vitess_statements") or not self.vitess_statements:
            raise_validation_error("Vitess storage not configured", status_code=503)
        result = self.vitess_statements.store_statement(content_hash, stmt_data)
        if result.success:
            logger.debug(f"[CLIENT_WRITE_STMT] Vitess SUCCESS: hash={content_hash}")
        else:
            logger.error(
                f"[CLIENT_WRITE_STMT] FAILED: content_hash={content_hash}, error={result.error}"
            )
            raise_validation_error("Storage service unavailable", status_code=503)

    def read_statement(self, content_hash: int) -> "StatementResponse":
        """Read statement snapshot from Vitess."""
        logger.debug(f"[CLIENT_READ_STMT] content_hash={content_hash}")
        if not hasattr(self, "vitess_statements") or not self.vitess_statements:
            raise_validation_error("Vitess storage not configured", status_code=503)
        response = self.vitess_statements.load_statement(content_hash)
        if response is not None:
            logger.debug(
                f"[CLIENT_READ_STMT] Vitess SUCCESS: content_hash={content_hash}"
            )
            return cast(StatementResponse, response)
        raise_validation_error(f"Statement not found: {content_hash}", status_code=404)

    def delete_metadata(self, metadata_type: MetadataType, content_hash: int) -> None:
        """Delete metadata content from Vitess when ref_count reaches 0."""
        if not hasattr(self, "vitess_metadata") or not self.vitess_metadata:
            raise_validation_error("Vitess storage not configured", status_code=503)
        content_type = metadata_type.value
        result = self.vitess_metadata.delete_metadata(content_hash, content_type)
        if not result.success:
            raise_validation_error("Storage service unavailable", status_code=503)

    def store_term_metadata(
        self, term: str, content_hash: int, content_type: str = "labels"
    ) -> None:
        """Store term metadata in Vitess."""
        if not hasattr(self, "vitess_metadata") or not self.vitess_metadata:
            raise_validation_error("Vitess storage not configured", status_code=503)
        result = self.vitess_metadata.store_metadata(content_hash, content_type, term)
        if not result.success:
            raise_validation_error("Storage service unavailable", status_code=503)

    def store_sitelink_metadata(self, title: str, content_hash: int) -> None:
        """Store sitelink metadata in Vitess."""
        if not hasattr(self, "vitess_sitelinks") or not self.vitess_sitelinks:
            raise_validation_error("Vitess storage not configured", status_code=503)
        result = self.vitess_sitelinks.store_sitelink(content_hash, title)
        if not result.success:
            raise_validation_error("Storage service unavailable", status_code=503)

    def load_sitelink_metadata(self, content_hash: int) -> str:
        """Load sitelink metadata from Vitess."""
        if not hasattr(self, "vitess_sitelinks") or not self.vitess_sitelinks:
            raise_validation_error("Vitess storage not configured", status_code=503)
        result = self.vitess_sitelinks.load_sitelink(content_hash)
        if result is None:
            raise_validation_error(
                f"Sitelink metadata not found for hash {content_hash}", status_code=404
            )
        return cast(str, result)

    def load_metadata(
        self, metadata_type: MetadataType, content_hash: int
    ) -> LoadResponse | None:
        """Load metadata by type from Vitess."""
        if not hasattr(self, "vitess_metadata") or not self.vitess_metadata:
            raise_validation_error("Vitess storage not configured", status_code=503)
        content_type = metadata_type.value
        result = self.vitess_metadata.load_metadata(content_hash, content_type)
        if result is None:
            return None
        from models.data.infrastructure.s3 import StringLoadResponse

        return StringLoadResponse(data=result)

    def store_reference(
        self, content_hash: int, reference_data: S3ReferenceData
    ) -> None:
        """Store a reference by its content hash in Vitess."""
        if not hasattr(self, "vitess_references") or not self.vitess_references:
            raise_validation_error("Vitess storage not configured", status_code=503)
        result = self.vitess_references.store_reference(content_hash, reference_data)
        if not result.success:
            raise_validation_error("Storage service unavailable", status_code=503)

    def load_reference(self, content_hash: int) -> S3ReferenceData:
        """Load a reference by its content hash from Vitess."""
        if not hasattr(self, "vitess_references") or not self.vitess_references:
            raise_validation_error("Vitess storage not configured", status_code=503)
        result = self.vitess_references.load_reference(content_hash)
        if result is None:
            raise_validation_error(
                f"Reference not found: {content_hash}", status_code=404
            )
        return cast(S3ReferenceData, result)

    def load_references_batch(
        self, content_hashes: list[int]
    ) -> list[S3ReferenceData | None]:
        """Load multiple references by their content hashes from Vitess."""
        if not hasattr(self, "vitess_references") or not self.vitess_references:
            raise_validation_error("Vitess storage not configured", status_code=503)
        return cast(
            list[S3ReferenceData | None],
            self.vitess_references.load_references_batch(content_hashes),
        )

    def store_qualifier(
        self, content_hash: int, qualifier_data: S3QualifierData
    ) -> None:
        """Store a qualifier by its content hash in Vitess."""
        if not hasattr(self, "vitess_qualifiers") or not self.vitess_qualifiers:
            raise_validation_error("Vitess storage not configured", status_code=503)
        result = self.vitess_qualifiers.store_qualifier(content_hash, qualifier_data)
        if not result.success:
            raise_validation_error("Storage service unavailable", status_code=503)

    def load_qualifier(self, content_hash: int) -> S3QualifierData:
        """Load a qualifier by its content hash from Vitess."""
        if not hasattr(self, "vitess_qualifiers") or not self.vitess_qualifiers:
            raise_validation_error("Vitess storage not configured", status_code=503)
        result = self.vitess_qualifiers.load_qualifier(content_hash)
        if result is None:
            raise_validation_error(
                f"Qualifier not found: {content_hash}", status_code=404
            )
        return cast(S3QualifierData, result)

    def load_qualifiers_batch(
        self, content_hashes: list[int]
    ) -> list[S3QualifierData | None]:
        """Load multiple qualifiers by their content hashes from Vitess."""
        if not hasattr(self, "vitess_qualifiers") or not self.vitess_qualifiers:
            raise_validation_error("Vitess storage not configured", status_code=503)
        return cast(
            list[S3QualifierData | None],
            self.vitess_qualifiers.load_qualifiers_batch(content_hashes),
        )

    def store_snak(self, content_hash: int, snak_data: S3SnakData) -> None:
        """Store a snak by its content hash in Vitess."""
        if not hasattr(self, "vitess_snaks") or not self.vitess_snaks:
            raise_validation_error("Vitess storage not configured", status_code=503)
        result = self.vitess_snaks.store_snak(content_hash, snak_data)
        if not result.success:
            raise_validation_error("Storage service unavailable", status_code=503)

    def load_snak(self, content_hash: int) -> S3SnakData:
        """Load a snak by its content hash from Vitess."""
        if not hasattr(self, "vitess_snaks") or not self.vitess_snaks:
            raise_validation_error("Vitess storage not configured", status_code=503)
        result = self.vitess_snaks.load_snak(content_hash)
        if result is None:
            raise_validation_error(f"Snak not found: {content_hash}", status_code=404)
        return cast(S3SnakData, result)

    def load_snaks_batch(self, content_hashes: list[int]) -> list[S3SnakData | None]:
        """Load multiple snaks by their content hashes from Vitess."""
        if not hasattr(self, "vitess_snaks") or not self.vitess_snaks:
            raise_validation_error("Vitess storage not configured", status_code=503)
        return cast(
            list[S3SnakData | None],
            self.vitess_snaks.load_snaks_batch(content_hashes),
        )

    def store_revision(self, content_hash: int, revision_data: S3RevisionData) -> None:
        """Store a revision by its content hash."""
        from models.infrastructure.s3.storage.revision_storage import RevisionStorage

        if not hasattr(self, "revisions") or self.revisions is None:
            self.revisions = RevisionStorage(connection_manager=self.connection_manager)
        result = self.revisions.store_revision(content_hash, revision_data)
        if not result.success:
            raise_validation_error("S3 storage service unavailable", status_code=503)

    def store_lemma(self, text: str, content_hash: int) -> None:
        """Store lemma text in Vitess."""
        if not hasattr(self, "vitess_metadata") or not self.vitess_metadata:
            raise_validation_error("Vitess storage not initialized", status_code=503)
        result = self.vitess_metadata.store_lemma(content_hash, text)
        if not result.success:
            raise_validation_error(
                "Vitess storage service unavailable", status_code=503
            )

    def load_revision(self, content_hash: int) -> S3RevisionData:
        """Load a revision by its content hash."""
        from models.infrastructure.s3.storage.revision_storage import RevisionStorage

        if not hasattr(self, "revisions") or self.revisions is None:
            self.revisions = RevisionStorage(connection_manager=self.connection_manager)
        return cast(S3RevisionData, self.revisions.load_revision(content_hash))

    def store_form_representation(self, text: str, content_hash: int) -> None:
        """Store form representation text in Vitess."""
        if not hasattr(self, "vitess_metadata") or not self.vitess_metadata:
            raise_validation_error("Vitess storage not initialized", status_code=503)
        result = self.vitess_metadata.store_form_representation(content_hash, text)
        if not result.success:
            raise_validation_error(
                "Vitess storage service unavailable", status_code=503
            )

    def store_sense_gloss(self, text: str, content_hash: int) -> None:
        """Store sense gloss text in Vitess."""
        if not hasattr(self, "vitess_metadata") or not self.vitess_metadata:
            raise_validation_error("Vitess storage not initialized", status_code=503)
        result = self.vitess_metadata.store_sense_gloss(content_hash, text)
        if not result.success:
            raise_validation_error(
                "Vitess storage service unavailable", status_code=503
            )

    def load_form_representations_batch(self, hashes: List[int]) -> List[Optional[str]]:
        """Load form representations by content hashes."""
        if not hasattr(self, "vitess_metadata") or not self.vitess_metadata:
            raise_validation_error("Vitess storage not initialized", status_code=503)
        return cast(
            list[str | None],
            self.vitess_metadata.load_form_representations_batch(hashes),
        )

    def load_sense_glosses_batch(self, hashes: List[int]) -> List[Optional[str]]:
        """Load sense glosses by content hashes."""
        if not hasattr(self, "vitess_metadata") or not self.vitess_metadata:
            raise_validation_error("Vitess storage not initialized", status_code=503)
        return cast(
            list[str | None], self.vitess_metadata.load_sense_glosses_batch(hashes)
        )

    def load_lemmas_batch(self, hashes: List[int]) -> List[Optional[str]]:
        """Load lemmas by content hashes."""
        if not hasattr(self, "vitess_metadata") or not self.vitess_metadata:
            raise_validation_error("Vitess storage not initialized", status_code=503)
        return cast(list[str | None], self.vitess_metadata.load_lemmas_batch(hashes))

    def disconnect(self) -> None:
        """Disconnect from S3 and release resources."""
        if self.connection_manager is not None:
            self.connection_manager.boto_client = None
            logger.info("S3Client disconnected")
