"""S3 storage client for entity and statement data."""

import json
from datetime import timezone, datetime
from typing import Any, Dict
import logging
from boto3.session import Session as BotoSession  # noqa
from botocore.exceptions import ClientError
from pydantic import Field
from models.validation.utils import raise_validation_error

from models.infrastructure.client import Client
from models.infrastructure.s3.connection import S3ConnectionManager
from models.s3_models import (
    RevisionData,
    S3Config,
    RevisionMetadata,
    RevisionReadResponse,
    StoredStatement,
)
from models.rest_api.entitybase.response import StatementResponse

logger = logging.getLogger(__name__)


class S3Client(Client):
    """Client for S3 storage operations."""

    config: S3Config
    connection_manager: S3ConnectionManager = Field(default=None, exclude=True)

    def __init__(self, config: S3Config, **kwargs: Any) -> None:
        super().__init__(config=config, **kwargs)
        manager = S3ConnectionManager(config=config)
        if manager is None:
            raise_validation_error("S3 service unavailable", status_code=503)
        self.connection_manager = manager
        self.connection_manager.connect()
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self) -> None:
        """Ensure the S3 bucket exists, creating it if necessary."""
        logger.debug(f"Ensuring bucket {self.config.bucket} exists")
        if not self.connection_manager or not self.connection_manager.boto_client:
            raise_validation_error("S3 service unavailable", status_code=503)
        try:
            self.connection_manager.boto_client.head_bucket(Bucket=self.config.bucket)
        except ClientError as e:
            if (
                e.response["Error"]["Code"] == "404"
                or e.response["Error"]["Code"] == "NoSuchBucket"
            ):
                try:
                    self.connection_manager.boto_client.create_bucket(
                        Bucket=self.config.bucket,
                        CreateBucketConfiguration={"LocationConstraint": "us-east-1"},
                    )
                except ClientError as ce:
                    print(f"Error creating bucket {self.config.bucket}: {ce}")
                    raise
            else:
                print(f"Error checking bucket {self.config.bucket}: {e}")
                raise
        except Exception as e:
            print(
                f"Unexpected error checking/creating bucket {self.config.bucket}: {e}"
            )
            raise

    def write_revision(
        self,
        entity_id: str,
        revision_id: int,
        data: Dict[str, Any],
        publication_state: str,
    ) -> RevisionMetadata:
        """Write entity revision data to S3."""
        if not self.connection_manager or not self.connection_manager.boto_client:
            raise_validation_error("S3 service unavailable", status_code=503)
        key = f"entities/{entity_id}/{revision_id}.json"
        self.connection_manager.boto_client.put_object(
            Bucket=self.config.bucket,
            Key=key,
            Body=json.dumps(data),
            Metadata={
                "schema_version": publication_state,
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        return RevisionMetadata(key=key)

    def read_revision(self, entity_id: str, revision_id: int) -> RevisionReadResponse:
        """Read S3 object and return parsed JSON."""
        if not self.connection_manager or not self.connection_manager.boto_client:
            raise_validation_error("S3 service unavailable", status_code=503)
        key = f"entities/{entity_id}/{revision_id}.json"
        response = self.connection_manager.boto_client.get_object(
            Bucket=self.config.bucket, Key=key
        )

        parsed_data = json.loads(response["Body"].read().decode("utf-8"))

        return RevisionReadResponse(
            entity_id=entity_id,
            revision_id=revision_id,
            data=RevisionData(**parsed_data),
            content=parsed_data.get("entity", {}),
        )

    def mark_published(
        self, entity_id: str, revision_id: int, publication_state: str
    ) -> None:
        """Update the publication state of an entity revision."""
        if not self.connection_manager or not self.connection_manager.boto_client:
            raise_validation_error("S3 service unavailable", status_code=503)
        key = f"{entity_id}/r{revision_id}.json"
        self.connection_manager.boto_client.copy_object(
            Bucket=self.config.bucket,
            CopySource={"Bucket": self.config.bucket, "Key": key},
            Key=key,
            Metadata={"publication_state": publication_state},
            MetadataDirective="REPLACE",
        )

    def read_full_revision(
        self, entity_id: str, revision_id: int
    ) -> RevisionReadResponse:
        """Read S3 object and return parsed full revision JSON."""
        if not self.connection_manager or not self.connection_manager.boto_client:
            raise_validation_error("S3 service unavailable", status_code=503)
        key = f"{entity_id}/r{revision_id}.json"
        response = self.connection_manager.boto_client.get_object(
            Bucket=self.config.bucket, Key=key
        )

        parsed_data: Dict[str, Any] = json.loads(
            response["Body"].read().decode("utf-8")
        )

        return RevisionReadResponse(
            entity_id=entity_id,
            revision_id=revision_id,
            data=RevisionData(**parsed_data),
            content=parsed_data.get("entity", {}),
        )

    def delete_statement(self, content_hash: int) -> None:
        """Delete statement from S3."""
        if not self.connection_manager or not self.connection_manager.boto_client:
            raise_validation_error("S3 service unavailable", status_code=503)
        key = f"statements/{content_hash}.json"
        self.connection_manager.boto_client.delete_object(
            Bucket=self.config.bucket, Key=key
        )

    def write_statement(
        self,
        content_hash: int,
        statement_data: Dict[str, Any],
        schema_version: str,
    ) -> None:
        """Write statement snapshot to S3.

        Stores statement at path: statements/{hash}.json.
        """
        if not self.connection_manager or not self.connection_manager.boto_client:
            raise_validation_error("S3 service unavailable", status_code=503)
        key = f"statements/{content_hash}.json"
        stored = StoredStatement(
            content_hash=content_hash,
            statement=statement_data["statement"],
            schema_version=schema_version,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        statement_json = json.dumps(stored.model_dump())

        # Enhanced pre-write validation logging
        logger.debug(f"S3 write_statement: bucket={self.config.bucket}, key={key}")
        # noinspection PyProtectedMember
        logger.debug(
            f"S3 client endpoint: {self.connection_manager.boto_client._endpoint.host}"
        )
        logger.debug(f"Statement data size: {len(statement_json)} bytes")
        logger.debug(f"Full statement data: {json.dumps(statement_data, indent=2)}")

        # Verify bucket exists before write
        try:
            self.connection_manager.boto_client.head_bucket(Bucket=self.config.bucket)
            logger.debug(f"S3 bucket {self.config.bucket} exists and is accessible")
        except Exception as bucket_error:
            logger.error(
                f"S3 bucket {self.config.bucket} not accessible: {bucket_error}"
            )
            raise

        try:
            response = self.connection_manager.boto_client.put_object(
                Bucket=self.config.bucket,
                Key=key,
                Body=statement_json,
                Metadata={"schema_version": schema_version},
            )

            # Enhanced response logging with S3 metadata
            logger.debug(
                f"S3 write_statement successful: bucket={self.config.bucket}, key={key}, "
                f"ETag={response.get('ETag')}, RequestId={response.get('ResponseMetadata', {}).get('RequestId')}"
            )

            # High Priority: Immediate verification by reading back written object
            try:
                verify_response = self.connection_manager.boto_client.get_object(
                    Bucket=self.config.bucket, Key=key
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
                    "bucket": self.config.bucket,
                    "key": key,
                    "statement_data_size": len(statement_json),
                    "s3_endpoint": self.connection_manager.boto_client._endpoint.host,
                },
                exc_info=True,
            )
            raise

    def read_statement(self, content_hash: int) -> StatementResponse:
        """Read statement snapshot from S3.

        Returns:
            Dict with keys: content_hash, statement, created_at.

        Raises:
            ClientError if statement not found.
        """
        if not self.connection_manager or not self.connection_manager.boto_client:
            raise_validation_error("S3 service unavailable", status_code=503)
        key = f"statements/{content_hash}.json"
        logger.debug(f"S3 read_statement: bucket={self.config.bucket}, key={key}")

        try:
            response = self.connection_manager.boto_client.get_object(
                Bucket=self.config.bucket, Key=key
            )
            parsed_data: Dict[str, Any] = json.loads(
                response["Body"].read().decode("utf-8")
            )

            stored_statement = StoredStatement.model_validate(parsed_data)

            logger.debug(
                f"S3 read_statement successful: bucket={self.config.bucket}, key={key}"
            )
            return StatementResponse(
                schema_version=stored_statement.schema_version,
                content_hash=stored_statement.content_hash,
                statement=stored_statement.statement,
                created_at=stored_statement.created_at,
            )
        except ClientError as e:
            error_code = e.response["Error"].get("Code", "Unknown")
            logger.error(
                "S3 ClientError in read_statement",
                extra={
                    "content_hash": content_hash,
                    "bucket": self.config.bucket,
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
                    "bucket": self.config.bucket,
                    "key": key,
                },
                exc_info=True,
            )
            raise

    def write_entity_revision(
        self,
        entity_id: str,
        revision_id: int,
        entity_type: str,
        revision_data: dict,
        edit_type: str = "",
        created_by: str = "rest-api",
        publication_state: str = "",
    ) -> int:
        """Write revision as part of redirect operations (no mark_pending/published flow)."""
        logger.debug(f"Writing entity revision {revision_id} for {entity_id}")
        if not self.connection_manager or not self.connection_manager.boto_client:
            raise_validation_error("S3 service unavailable", status_code=503)
        full_data = {
            "schema_version": "1.2.0",
            "revision_id": revision_id,
            "created_at": datetime.now(timezone.utc).isoformat() + "Z",
            "created_by": created_by,
            "is_mass_edit": False,
            "edit_type": edit_type,
            "entity_type": entity_type,
            "is_semi_protected": False,
            "is_locked": False,
            "is_archived": False,
            "is_dangling": False,
            "is_mass_edit_protected": False,
            "is_deleted": False,
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

        key = f"entities/{entity_id}/{revision_id}.json"
        self.connection_manager.boto_client.put_object(
            Bucket=self.config.bucket,
            Key=key,
            Body=json.dumps(full_data),
            Metadata={
                "schema_version": publication_state,
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        return revision_id

    def delete_metadata(self, metadata_type: str, content_hash: int) -> None:
        """Delete metadata content from S3 when ref_count reaches 0."""
        key = f"metadata/{metadata_type}/{content_hash}.json"
        try:
            self.connection_manager.boto_client.delete_object(
                Bucket=self.config.bucket, Key=key
            )
            logger.debug(f"S3 delete_metadata: bucket={self.config.bucket}, key={key}")
        except Exception as e:
            logger.error(
                f"S3 delete_metadata failed: bucket={self.config.bucket}, key={key}, error={e}"
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
        bucket = "wikibase-terms"

        try:
            self.connection_manager.boto_client.put_object(
                Bucket=bucket,
                Key=key,
                Body=term.encode("utf-8"),
                ContentType="text/plain",
                Metadata={"content_hash": str(content_hash)},
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
        bucket = "wikibase-terms"

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
                Metadata={"content_hash": str(content_hash)},
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
        bucket = "wikibase-sitelinks"

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
        return ""  # unreachable, but for linter
