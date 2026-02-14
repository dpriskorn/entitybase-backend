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
from models.infrastructure.s3.storage.metadata_storage import MetadataStorage
from models.infrastructure.s3.storage.qualifier_storage import QualifierStorage
from models.infrastructure.s3.storage.reference_storage import ReferenceStorage
from models.infrastructure.s3.storage.revision_storage import RevisionStorage
from models.infrastructure.s3.storage.snak_storage import SnakStorage
from models.infrastructure.s3.storage.statement_storage import StatementStorage
from models.infrastructure.vitess.repositories.revision import RevisionRepository
from models.data.rest_api.v1.entitybase.response import StatementResponse
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)


class MyS3Client(Client):
    """Client for S3 storage operations."""

    vitess_client: Optional[Any] = Field(default=None, exclude=True)
    connection_manager: Optional[S3ConnectionManager] = Field(
        default=None, exclude=True
    )  # type: ignore[override]
    revisions: Any = Field(default=None, exclude=True)
    statements: Any = Field(default=None, exclude=True)
    metadata: Any = Field(default=None, exclude=True)
    references: Any = Field(default=None, exclude=True)
    qualifiers: Any = Field(default=None, exclude=True)
    snaks: Any = Field(default=None, exclude=True)
    lexemes: Any = Field(default=None, exclude=True)

    def model_post_init(self, context: Any) -> None:
        # noinspection PyTypeChecker
        manager = S3ConnectionManager(config=self.config)
        if manager is None:
            raise_validation_error("S3 service unavailable", status_code=503)
        self.connection_manager = manager  # type: ignore[assignment]
        self.connection_manager.connect()
        # self._ensure_bucket_exists()

        # Initialize storage components
        self.revisions = RevisionStorage(connection_manager=self.connection_manager)
        self.statements = StatementStorage(connection_manager=self.connection_manager)
        self.metadata = MetadataStorage(connection_manager=self.connection_manager)
        self.references = ReferenceStorage(connection_manager=self.connection_manager)
        self.qualifiers = QualifierStorage(connection_manager=self.connection_manager)
        self.snaks = SnakStorage(connection_manager=self.connection_manager)

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
        internal_id = self.vitess_client.id_resolver.resolve_id(entity_id)
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
        """Delete statement from S3."""
        result = self.statements.delete_statement(content_hash)
        if not result.success:
            raise_validation_error("S3 storage service unavailable", status_code=503)

    def write_statement(
        self,
        content_hash: int,
        statement_data: dict[str, Any],
        schema_version: str,
    ) -> None:
        """Write statement snapshot to S3."""
        logger.debug(
            f"[S3_CLIENT_WRITE_STMT] content_hash={content_hash}, "
            f"schema_version={schema_version}, data_keys={list(statement_data.keys())}"
        )
        result = self.statements.store_statement(
            content_hash, statement_data, schema_version
        )
        if result.success:
            logger.debug(f"[S3_CLIENT_WRITE_STMT] SUCCESS: content_hash={content_hash}")
        else:
            logger.error(
                f"[S3_CLIENT_WRITE_STMT] FAILED: content_hash={content_hash}, error={result.error}"
            )
            raise_validation_error("S3 storage service unavailable", status_code=503)

    def read_statement(self, content_hash: int) -> "StatementResponse":
        """Read statement snapshot from S3."""
        logger.debug(f"[S3_CLIENT_READ_STMT] content_hash={content_hash}")
        try:
            response = cast(
                StatementResponse, self.statements.load_statement(content_hash)
            )
            logger.debug(f"[S3_CLIENT_READ_STMT] SUCCESS: content_hash={content_hash}")
            return response
        except Exception as e:
            logger.error(
                f"[S3_CLIENT_READ_STMT] FAILED: content_hash={content_hash}, "
                f"error={type(e).__name__}: {e}"
            )
            raise

    def delete_metadata(self, metadata_type: MetadataType, content_hash: int) -> None:
        """Delete metadata content from S3 when ref_count reaches 0."""
        result = self.metadata.delete_metadata(metadata_type, content_hash)
        if not result.success:
            logger.error(
                f"S3 delete_metadata failed for {metadata_type}:{content_hash}"
            )

    def store_term_metadata(self, term: str, content_hash: int) -> None:
        """Store term metadata as plain UTF-8 text in S3."""
        # Assume term type is "labels" for now, but could be generalized
        # Since old method didn't specify type, use "labels" as default
        result = self.metadata.store_metadata(MetadataType.LABELS, content_hash, term)
        if not result.success:
            raise_validation_error("S3 storage service unavailable", status_code=503)

    def load_term_metadata(self, content_hash: int) -> str:
        """Load term metadata as plain UTF-8 text from S3."""
        result = self.metadata.load_metadata(MetadataType.LABELS, content_hash)
        if result is None:
            raise_validation_error(
                f"Term metadata not found for hash {content_hash}", status_code=404
            )
        return cast(str, result.data)

    def store_sitelink_metadata(self, title: str, content_hash: int) -> None:
        """Store sitelink metadata as plain UTF-8 text in S3."""
        result = self.metadata.store_metadata(
            MetadataType.SITELINKS, content_hash, title
        )
        if not result.success:
            raise_validation_error("S3 storage service unavailable", status_code=503)

    def load_sitelink_metadata(self, content_hash: int) -> str:
        """Load sitelink metadata as plain UTF-8 text from S3."""
        result = self.metadata.load_metadata(MetadataType.SITELINKS, content_hash)
        if result is None:
            raise_validation_error(
                f"Sitelink metadata not found for hash {content_hash}", status_code=404
            )
        return cast(str, result.data)

    def load_metadata(
        self, metadata_type: MetadataType, content_hash: int
    ) -> LoadResponse | None:
        """Load metadata by type."""
        return cast(
            StringLoadResponse | DictLoadResponse | None,
            self.metadata.load_metadata(metadata_type, content_hash),
        )

    def store_reference(
        self, content_hash: int, reference_data: S3ReferenceData
    ) -> None:
        """Store a reference by its content hash."""
        result = self.references.store_reference(content_hash, reference_data)
        if not result.success:
            raise_validation_error("S3 storage service unavailable", status_code=503)

    def load_reference(self, content_hash: int) -> S3ReferenceData:
        """Load a reference by its content hash."""
        return cast(S3ReferenceData, self.references.load_reference(content_hash))

    def load_references_batch(
        self, content_hashes: list[int]
    ) -> list[S3ReferenceData | None]:
        """Load multiple references by their content hashes."""
        return cast(
            list[S3ReferenceData | None],
            self.references.load_references_batch(content_hashes),
        )

    def store_qualifier(
        self, content_hash: int, qualifier_data: S3QualifierData
    ) -> None:
        """Store a qualifier by its content hash."""
        result = self.qualifiers.store_qualifier(content_hash, qualifier_data)
        if not result.success:
            raise_validation_error("S3 storage service unavailable", status_code=503)

    def load_qualifier(self, content_hash: int) -> S3QualifierData:
        """Load a qualifier by its content hash."""
        return cast(S3QualifierData, self.qualifiers.load_qualifier(content_hash))

    def load_qualifiers_batch(
        self, content_hashes: list[int]
    ) -> list[S3QualifierData | None]:
        """Load multiple qualifiers by their content hashes."""
        return cast(
            list[S3QualifierData | None],
            self.qualifiers.load_qualifiers_batch(content_hashes),
        )

    def store_snak(self, content_hash: int, snak_data: S3SnakData) -> None:
        """Store a snak by its content hash."""
        result = self.snaks.store_snak(content_hash, snak_data)
        if not result.success:
            raise_validation_error("S3 storage service unavailable", status_code=503)

    def load_snak(self, content_hash: int) -> S3SnakData:
        """Load a snak by its content hash."""
        return cast(S3SnakData, self.snaks.load_snak(content_hash))

    def load_snaks_batch(self, content_hashes: list[int]) -> list[S3SnakData | None]:
        """Load multiple snaks by their content hashes."""
        return cast(
            list[S3SnakData | None], self.snaks.load_snaks_batch(content_hashes)
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
        """Store lemma text in terms bucket."""
        from models.infrastructure.s3.storage.lexeme_storage import LexemeStorage

        if not hasattr(self, "lexemes") or self.lexemes is None:
            self.lexemes = LexemeStorage(connection_manager=self.connection_manager)
        result = self.lexemes.store_lemma(text, content_hash)
        if not result.success:
            raise_validation_error("S3 storage service unavailable", status_code=503)

    def load_revision(self, content_hash: int) -> S3RevisionData:
        """Load a revision by its content hash."""
        from models.infrastructure.s3.storage.revision_storage import RevisionStorage

        if not hasattr(self, "revisions") or self.revisions is None:
            self.revisions = RevisionStorage(connection_manager=self.connection_manager)
        return cast(S3RevisionData, self.revisions.load_revision(content_hash))

    def store_form_representation(self, text: str, content_hash: int) -> None:
        """Store form representation text in terms bucket."""
        from models.infrastructure.s3.storage.lexeme_storage import LexemeStorage

        if not hasattr(self, "lexemes") or self.lexemes is None:
            self.lexemes = LexemeStorage(connection_manager=self.connection_manager)
        result = self.lexemes.store_form_representation(text, content_hash)
        if not result.success:
            raise_validation_error("S3 storage service unavailable", status_code=503)

    def store_sense_gloss(self, text: str, content_hash: int) -> None:
        """Store sense gloss text in terms bucket."""
        from models.infrastructure.s3.storage.lexeme_storage import LexemeStorage

        if not hasattr(self, "lexemes") or self.lexemes is None:
            self.lexemes = LexemeStorage(connection_manager=self.connection_manager)
        result = self.lexemes.store_sense_gloss(text, content_hash)
        if not result.success:
            raise_validation_error("S3 storage service unavailable", status_code=503)

    def load_form_representations_batch(self, hashes: List[int]) -> List[Optional[str]]:
        """Load form representations by content hashes."""
        from models.infrastructure.s3.storage.lexeme_storage import LexemeStorage

        if not hasattr(self, "lexemes") or self.lexemes is None:
            self.lexemes = LexemeStorage(connection_manager=self.connection_manager)
        return cast(
            list[str | None], self.lexemes.load_form_representations_batch(hashes)
        )

    def load_sense_glosses_batch(self, hashes: List[int]) -> List[Optional[str]]:
        """Load sense glosses by content hashes."""
        from models.infrastructure.s3.storage.lexeme_storage import LexemeStorage

        if not hasattr(self, "lexemes") or self.lexemes is None:
            self.lexemes = LexemeStorage(connection_manager=self.connection_manager)
        return cast(list[str | None], self.lexemes.load_sense_glosses_batch(hashes))

    def load_lemmas_batch(self, hashes: List[int]) -> List[Optional[str]]:
        """Load lemmas by content hashes."""
        from models.infrastructure.s3.storage.lexeme_storage import LexemeStorage

        if not hasattr(self, "lexemes") or self.lexemes is None:
            self.lexemes = LexemeStorage(connection_manager=self.connection_manager)
        return cast(list[str | None], self.lexemes.load_lemmas_batch(hashes))

    def disconnect(self) -> None:
        """Disconnect from S3 and release resources."""
        if self.connection_manager is not None:
            self.connection_manager.boto_client = None
            logger.info("S3Client disconnected")
