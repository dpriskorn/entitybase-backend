"""S3 storage client for entity and statement data."""

import json
import logging
from datetime import timezone, datetime
from typing import Any, Dict, Optional, TYPE_CHECKING

from boto3.session import Session as BotoSession  # noqa  # type: ignore[import-untyped]
from botocore.exceptions import ClientError  # type: ignore[import-untyped]
from pydantic import Field

from models.common import OperationResult
from models.config.settings import settings
from models.infrastructure.client import Client
from models.infrastructure.s3.connection import S3ConnectionManager
from models.infrastructure.s3.metadata_storage import MetadataStorage
from models.infrastructure.s3.revision_storage import RevisionStorage
from models.infrastructure.s3.statement_storage import StatementStorage
from models.rest_api.entitybase.response import StatementResponse
from models.infrastructure.s3.config import S3Config
from models.s3_models import (
    RevisionData,
    RevisionReadResponse,
    StoredStatement,
    S3QualifierData,
    S3ReferenceData,
)
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

    # def _ensure_bucket_exists(self) -> None:
    #     """Ensure the S3 bucket exists, creating it if necessary."""
    #     logger.debug(f"Ensuring bucket {bucket} exists")
    #     if not self.connection_manager or not self.connection_manager.boto_client:
    #         raise_validation_error("S3 service unavailable", status_code=503)
    #     try:
    #         self.connection_manager.boto_client.head_bucket(Bucket=bucket)
    #     except ClientError as e:
    #         if (
    #             e.response["Error"]["Code"] == "404"
    #             or e.response["Error"]["Code"] == "NoSuchBucket"
    #         ):
    #             try:
    #                 # noinspection PyTypeChecker
    #                 self.connection_manager.boto_client.create_bucket(
    #                     Bucket=bucket,
    #                     CreateBucketConfiguration={"LocationConstraint": "us-east-1"},  # type: ignore[typeddict-item]
    #                 )
    #             except ClientError as ce:
    #                 print(f"Error creating bucket {bucket}: {ce}")
    #                 raise
    #         else:
    #             print(f"Error checking bucket {bucket}: {e}")
    #             raise
    #     except Exception as e:
    #         print(
    #             f"Unexpected error checking/creating bucket {bucket}: {e}"
    #         )
    #         raise

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

    def write_entity_revision(
        self,
        entity_id: str,
        revision_id: int,
        revision_data: RevisionData,
    ) -> int:
        """Write revision as part of redirect operations (no mark_pending/published flow)."""
        logger.debug(f"Writing entity revision {revision_id} for {entity_id}")
        if not self.connection_manager or not self.connection_manager.boto_client:
            raise_validation_error("S3 service unavailable", status_code=503)

        full_data = {
            "schema_version": settings.s3_schema_revision_version,
            "revision_id": revision_id,
            "created_at": datetime.now(timezone.utc).isoformat() + "Z",
            "created_by": created_by,
            "is_mass_edit": False,
            "edit_type": edit_type,
            "entity_type": entity_type,
            "is_redirect": False,
            "statements": [],
            "properties": [],
            "property_counts": {},
            "entity": {
                "id": revision_data.get("id"),
                "type": entity_type,
                "labels": revision_data.get("labels"),
                "descriptions": revision_data.get("descriptions"),
                "aliases": revision_data.get("aliases"),
                "sitelinks": revision_data.get("sitelinks"),
            },
        }

        key = f"entities/{entity_id}/{revision_id}"
        self.connection_manager.boto_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=full_data,
            Metadata={
                "schema_version": publication_state,
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        return revision_id

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

    def store_reference(
        self, content_hash: int, reference_data: S3ReferenceData
    ) -> None:
        """Store a reference by its content hash.

        Args:
            content_hash: Rapidhash of the reference content.
            reference_data: Full reference JSON dict.
        """
        if not self.connection_manager or not self.connection_manager.boto_client:
            raise_validation_error("S3 service unavailable", status_code=503)
        bucket = settings.s3_references_bucket
        key = f"{content_hash}"
        try:
            self.connection_manager.boto_client.put_object(
                Bucket=bucket,
                Key=key,
                Body=reference_data.model_dump(mode="json"),
                ContentType="application/json",
                Metadata={"content_hash": str(content_hash)},
            )
            logger.debug(f"S3 reference stored: bucket={bucket}, key={key}")
        except ClientError as e:
            logger.error(
                f"S3 store_reference failed: bucket={bucket}, key={key}, error={e}"
            )
            raise
        except Exception as e:
            logger.error(
                f"S3 store_reference failed: bucket={bucket}, key={key}, error={e}"
            )
            raise

    def load_reference(self, content_hash: int) -> S3ReferenceData:
        """Load a reference by its content hash.

        Args:
            content_hash: Rapidhash of the reference content.

        Returns:
            ReferenceModel instance.
        """
        if not self.connection_manager or not self.connection_manager.boto_client:
            raise_validation_error("S3 service unavailable", status_code=503)
        bucket = settings.s3_references_bucket
        key = f"{content_hash}"
        try:
            response = self.connection_manager.boto_client.get_object(
                Bucket=bucket, Key=key
            )
            data = json.loads(response["Body"].read().decode("utf-8"))
            logger.debug(f"S3 reference loaded: bucket={bucket}, key={key}")
            return S3ReferenceData(**data)
        except ClientError as e:
            if e.response["Error"].get("Code") in ["NoSuchKey", "404"]:
                logger.warning(f"S3 reference not found: bucket={bucket}, key={key}")
                raise
            else:
                logger.error(
                    f"S3 load_reference failed: bucket={bucket}, key={key}, error={e}"
                )
                raise
        except Exception as e:
            logger.error(
                f"S3 load_reference failed: bucket={bucket}, key={key}, error={e}"
            )
            raise

    def load_references_batch(
        self, content_hashes: list[int]
    ) -> list[S3ReferenceData | None]:
        """Load multiple references by their content hashes.

        Args:
            content_hashes: List of rapidhashes.

        Returns:
            List of ReferenceModel instances, in same order. None for missing.
        """
        results: list[S3ReferenceData | None] = []
        for h in content_hashes:
            try:
                ref = self.load_reference(h)
                results.append(ref)
            except ClientError:
                results.append(None)
        return results

    def store_qualifier(
        self, content_hash: int, qualifier_data: S3QualifierData
    ) -> None:
        """Store a qualifier by its content hash.

        Args:
            content_hash: Rapidhash of the qualifier content.
            qualifier_data: Full qualifier JSON dict.
        """
        if not self.connection_manager or not self.connection_manager.boto_client:
            raise_validation_error("S3 service unavailable", status_code=503)
        bucket = settings.s3_qualifiers_bucket
        key = f"{content_hash}"
        try:
            self.connection_manager.boto_client.put_object(
                Bucket=bucket,
                Key=key,
                Body=qualifier_data.model_dump(mode="json"),
                ContentType="application/json",
                Metadata={"content_hash": str(content_hash)},
            )
            logger.debug(f"S3 qualifier stored: bucket={bucket}, key={key}")
        except ClientError as e:
            logger.error(
                f"S3 store_qualifier failed: bucket={bucket}, key={key}, error={e}"
            )
            raise
        except Exception as e:
            logger.error(
                f"S3 store_qualifier failed: bucket={bucket}, key={key}, error={e}"
            )
            raise

    def load_qualifier(self, content_hash: int) -> S3QualifierData:
        """Load a qualifier by its content hash.

        Args:
            content_hash: Rapidhash of the qualifier content.

        Returns:
            QualifierModel instance.
        """
        if not self.connection_manager or not self.connection_manager.boto_client:
            raise_validation_error("S3 service unavailable", status_code=503)
        bucket = settings.s3_qualifiers_bucket
        key = f"{content_hash}"
        try:
            response = self.connection_manager.boto_client.get_object(
                Bucket=bucket, Key=key
            )
            data = json.loads(response["Body"].read().decode("utf-8"))
            logger.debug(f"S3 qualifier loaded: bucket={bucket}, key={key}")
            return S3QualifierData(**data)
        except ClientError as e:
            if e.response["Error"].get("Code") in ["NoSuchKey", "404"]:
                logger.warning(f"S3 qualifier not found: bucket={bucket}, key={key}")
                raise
            else:
                logger.error(
                    f"S3 load_qualifier failed: bucket={bucket}, key={key}, error={e}"
                )
                raise
        except Exception as e:
            logger.error(
                f"S3 load_qualifier failed: bucket={bucket}, key={key}, error={e}"
            )
            raise

    def load_qualifiers_batch(
        self, content_hashes: list[int]
    ) -> list[S3QualifierData | None]:
        """Load multiple qualifiers by their content hashes.

        Args:
            content_hashes: List of rapidhashes.

        Returns:
            List of QualifierModel instances, in same order. None for missing.
        """
        results: list[S3QualifierData | None] = []
        for h in content_hashes:
            try:
                qual = self.load_qualifier(h)
                results.append(qual)
            except ClientError:
                results.append(None)
        return results


MyS3Client.model_rebuild()
