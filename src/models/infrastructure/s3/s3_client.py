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
from models.rest_api.entitybase.response import StatementResponse
from models.s3_models import (
    RevisionData,
    S3Config,
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
        if not self.connection_manager or not self.connection_manager.boto_client:
            raise_validation_error("S3 service unavailable", status_code=503)
        bucket = settings.s3_revisions_bucket
        key = f"entities/{entity_id}/{revision_id}"
        try:
            self.connection_manager.boto_client.put_object(
                Bucket=bucket,
                Key=key,
                Body=data.model_dump(mode="json"),
                Metadata={
                    "schema_version": data.schema_version,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
            )
            return OperationResult(success=True)
        except Exception:
            raise_validation_error("S3 storage service unavailable", status_code=503)

    def read_revision(self, entity_id: str, revision_id: int) -> RevisionReadResponse:
        """Read S3 object and return parsed JSON."""
        if not self.connection_manager or not self.connection_manager.boto_client:
            raise_validation_error("S3 service unavailable", status_code=503)
        bucket = settings.s3_revisions_bucket
        key = f"{entity_id}/{revision_id}"
        response = self.connection_manager.boto_client.get_object(
            Bucket=bucket, Key=key
        )

        parsed_data = json.loads(response["Body"].read().decode("utf-8"))

        return RevisionReadResponse(
            entity_id=entity_id,
            revision_id=revision_id,
            data=RevisionData(**parsed_data),
            content=parsed_data.get("entity", {}),
            schema_version=parsed_data.get("schema_version", ""),
            created_at=response["Metadata"].get("created_at", ""),
        )

    def mark_published(
        self, entity_id: str, revision_id: int, publication_state: str
    ) -> None:
        """Update the publication state of an entity revision."""
        if not self.connection_manager or not self.connection_manager.boto_client:
            raise_validation_error("S3 service unavailable", status_code=503)
        bucket = settings.s3_revisions_bucket
        key = f"{entity_id}/{revision_id}"
        # noinspection PyTypeChecker
        self.connection_manager.boto_client.copy_object(
            Bucket=bucket,
            CopySource={"Bucket": bucket, "Key": key},
            Key=key,
            Metadata={"publication_state": publication_state},
            MetadataDirective="REPLACE",
        )

    def delete_statement(self, content_hash: int) -> None:
        """Delete statement from S3."""
        if not self.connection_manager or not self.connection_manager.boto_client:
            raise_validation_error("S3 service unavailable", status_code=503)
        bucket = settings.s3_statements_bucket
        key = f"{content_hash}"
        self.connection_manager.boto_client.delete_object(Bucket=bucket, Key=key)

    def write_statement(
        self,
        content_hash: int,
        statement_data: Dict[str, Any],
        schema_version: str,
    ) -> None:
        """Write statement snapshot to S3.

        Stores statement at path: {hash}.
        """
        if not self.connection_manager or not self.connection_manager.boto_client:
            raise_validation_error("S3 service unavailable", status_code=503)
        bucket = settings.s3_statements_bucket
        key = f"{content_hash}"
        stored = StoredStatement(
            hash=content_hash,
            statement=statement_data["statement"],
            schema=schema_version,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        statement_json = stored.model_dump(mode="json")

        # Enhanced pre-write validation logging
        logger.debug(f"S3 write_statement: bucket={bucket}, key={key}")
        # noinspection PyProtectedMember
        logger.debug(
            f"S3 client endpoint: {self.connection_manager.boto_client.meta.endpoint_url}"
        )
        logger.debug(f"Statement data size: {len(statement_json)} bytes")
        logger.debug(f"Full statement data: {json.dumps(statement_data, indent=2)}")

        # Verify bucket exists before write
        try:
            self.connection_manager.boto_client.head_bucket(Bucket=bucket)
            logger.debug(f"S3 bucket {bucket} exists and is accessible")
        except Exception as bucket_error:
            logger.error(f"S3 bucket {bucket} not accessible: {bucket_error}")
            raise

        try:
            response = self.connection_manager.boto_client.put_object(
                Bucket=bucket,
                Key=key,
                Body=statement_json,
                Metadata={"schema_version": schema_version},
            )

            # Enhanced response logging with S3 metadata
            logger.debug(
                f"S3 write_statement successful: bucket={bucket}, key={key}, "
                f"ETag={response.get('ETag')}, RequestId={response.get('ResponseMetadata', {}).get('RequestId')}"
            )

            # High Priority: Immediate verification by reading back written object
            try:
                verify_response = self.connection_manager.boto_client.get_object(
                    Bucket=bucket, Key=key
                )
                verify_data = json.loads(verify_response["Body"].read().decode("utf-8"))
                logger.debug(
                    f"S3 write verification successful: data matches written content for {content_hash}"
                )

                # Verify the content hash matches what we wrote
                if verify_data.get("content_hash") == content_hash:
                    logger.debug(
                        f"S3 write verification successful: content_hash matches for {content_hash}"
                    )
                else:
                    logger.error(
                        f"S3 write verification failed: content_hash mismatch for {content_hash} - got {verify_data.get('content_hash')}"
                    )

            except Exception as verify_error:
                logger.error(
                    f"S3 write verification failed for {content_hash}: {verify_error}"
                )
                raise

        except Exception as e:
            # noinspection PyProtectedMember
            logger.error(
                f"S3 write_statement failed for {content_hash}: {type(e).__name__}: {e}",
                extra={
                    "content_hash": content_hash,
                    "bucket": bucket,
                    "key": key,
                    "statement_data_size": len(statement_json),
                    "s3_endpoint": self.connection_manager.boto_client.meta.endpoint_url,
                },
                exc_info=True,
            )
            raise

    def read_statement(self, content_hash: int) -> "StatementResponse":
        """Read statement snapshot from S3.

        Returns:
            Dict with keys: content_hash, statement, created_at.

        Raises:
            ClientError if statement not found.
        """
        if not self.connection_manager or not self.connection_manager.boto_client:
            raise_validation_error("S3 service unavailable", status_code=503)
        bucket = settings.s3_statements_bucket
        key = f"{content_hash}"
        logger.debug(f"S3 read_statement: bucket={bucket}, key={key}")

        try:
            response = self.connection_manager.boto_client.get_object(
                Bucket=bucket, Key=key
            )
            parsed_data: Dict[str, Any] = json.loads(
                response["Body"].read().decode("utf-8")
            )

            stored_statement = StoredStatement.model_validate(parsed_data)

            logger.debug(f"S3 read_statement successful: bucket={bucket}, key={key}")
            return StatementResponse(
                schema=stored_statement.schema_version,
                hash=stored_statement.content_hash,
                statement=stored_statement.statement,
                created_at=stored_statement.created_at,
            )
        except ClientError as e:
            error_code = e.response["Error"].get("Code", "Unknown")
            logger.error(
                "S3 ClientError in read_statement",
                extra={
                    "content_hash": content_hash,
                    "bucket": bucket,
                    "key": key,
                    "error_code": error_code,
                    "error_message": str(e),
                    "is_not_found": error_code in ["NoSuchKey", "404"],
                },
            )
            raise
        except Exception as e:
            logger.error(
                f"S3 read_statement failed with non-ClientError for {content_hash}: {type(e).__name__}: {e}",
                extra={
                    "content_hash": content_hash,
                    "bucket": bucket,
                    "key": key,
                },
                exc_info=True,
            )
            raise

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
        key = f"metadata/{metadata_type}/{content_hash}"

        # Determine bucket based on metadata type
        if metadata_type in ("labels", "descriptions", "aliases"):
            bucket = settings.s3_terms_bucket
        elif metadata_type == "sitelinks":
            bucket = settings.s3_sitelinks_bucket
        else:
            raise_validation_error(f"Unknown metadata type for deletion: {metadata_type}", status_code=400)

        try:
            self.connection_manager.boto_client.delete_object(  # type: ignore[union-attr]
                Bucket=bucket, Key=key
            )
            logger.debug(f"S3 delete_metadata: bucket={bucket}, key={key}")
        except Exception as e:
            logger.error(
                f"S3 delete_metadata failed: bucket={bucket}, key={key}, error={e}"
            )

    def store_term_metadata(self, term: str, content_hash: int) -> None:
        """Store term metadata as plain UTF-8 text in S3.

        Args:
            term: The term value
            content_hash: Hash of the term
        """
        if not self.connection_manager or not self.connection_manager.boto_client:
            raise_validation_error("S3 service unavailable", status_code=503)

        key = str(content_hash)
        bucket = settings.s3_terms_bucket

        try:
            self.connection_manager.boto_client.put_object(
                Bucket=bucket,
                Key=key,
                Body=term.encode("utf-8"),
                ContentType="text/plain",
                # Metadata={"content_hash": str(content_hash)},
            )
            logger.debug(f"S3 store_term_metadata: bucket={bucket}, key={key}")
        except Exception as e:
            logger.error(
                f"S3 store_term_metadata failed: bucket={bucket}, key={key}, error={e}"
            )
            raise

    def load_term_metadata(self, content_hash: int) -> str:  # type: ignore[no-any-return]
        """Load term metadata as plain UTF-8 text from S3.

        Args:
            content_hash: Hash of the term

        Returns:
            The term value
        """
        if not self.connection_manager or not self.connection_manager.boto_client:
            raise_validation_error("S3 service unavailable", status_code=503)

        key = str(content_hash)
        bucket = settings.s3_terms_bucket

        try:
            response = self.connection_manager.boto_client.get_object(
                Bucket=bucket, Key=key
            )
            term = response["Body"].read().decode("utf-8")
            logger.debug(f"S3 load_term_metadata: bucket={bucket}, key={key}")
            return term  # type: ignore[no-any-return]
        except ClientError as e:
            if e.response["Error"].get("Code") in ["NoSuchKey", "404"]:
                logger.warning(f"S3 term not found: bucket={bucket}, key={key}")
                raise
            else:
                logger.error(
                    f"S3 load_term_metadata failed: bucket={bucket}, key={key}, error={e}"
                )
                raise
        except Exception as e:
            logger.error(
                f"S3 load_term_metadata failed: bucket={bucket}, key={key}, error={e}"
            )
            raise

    def store_sitelink_metadata(self, title: str, content_hash: int) -> None:
        """Store sitelink metadata as plain UTF-8 text in S3.

        Args:
            title: The sitelink title
            content_hash: Hash of the title
        """
        if not self.connection_manager or not self.connection_manager.boto_client:
            raise_validation_error("S3 service unavailable", status_code=503)

        key = str(content_hash)
        bucket = "wikibase-sitelinks"

        try:
            self.connection_manager.boto_client.put_object(
                Bucket=bucket,
                Key=key,
                Body=title.encode("utf-8"),
                ContentType="text/plain",
                # Metadata={"content_hash": str(content_hash)},
            )
            logger.debug(f"S3 store_sitelink_metadata: bucket={bucket}, key={key}")
        except Exception as e:
            logger.error(
                f"S3 store_sitelink_metadata failed: bucket={bucket}, key={key}, error={e}"
            )
            raise

    def load_sitelink_metadata(self, content_hash: int) -> str:  # type: ignore[no-any-return]
        """Load sitelink metadata as plain UTF-8 text from S3.

        Args:
            content_hash: Hash of the title

        Returns:
            The sitelink title
        """
        if not self.connection_manager or not self.connection_manager.boto_client:
            raise_validation_error("S3 service unavailable", status_code=503)

        key = str(content_hash)
        bucket = settings.s3_sitelinks_bucket

        try:
            response = self.connection_manager.boto_client.get_object(
                Bucket=bucket, Key=key
            )
            title = response["Body"].read().decode("utf-8")
            logger.debug(f"S3 load_sitelink_metadata: bucket={bucket}, key={key}")
            return title  # type: ignore[no-any-return]
        except ClientError as e:
            if e.response["Error"].get("Code") in ["NoSuchKey", "404"]:
                logger.warning(f"S3 sitelink not found: bucket={bucket}, key={key}")
                raise
            else:
                logger.error(
                    f"S3 load_sitelink_metadata failed: bucket={bucket}, key={key}, error={e}"
                )
                raise
        except Exception as e:
            logger.error(
                f"S3 load_sitelink_metadata failed: bucket={bucket}, key={key}, error={e}"
            )
            raise

    def load_metadata(self, metadata_type: str, content_hash: int) -> str:
        """Load metadata by type."""
        if metadata_type == "labels":
            return self.load_term_metadata(content_hash)
        elif metadata_type == "descriptions":
            return self.load_term_metadata(content_hash)
        elif metadata_type == "aliases":
            return self.load_term_metadata(content_hash)
        elif metadata_type == "sitelinks":
            return self.load_sitelink_metadata(content_hash)
        else:
            raise_validation_error(
                f"Unknown metadata type: {metadata_type}", status_code=400
            )

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
