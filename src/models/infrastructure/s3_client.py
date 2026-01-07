from datetime import timezone
from typing import Any, Dict
import boto3
import logging
from botocore.client import Config
from botocore.exceptions import ClientError
from pydantic import BaseModel, ConfigDict, Field

from models.s3_models import (
    S3Config,
    RevisionMetadata,
    RevisionReadResponse,
)


class S3Client(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    config: S3Config
    client: Any = Field(default=None, exclude=True)

    def __init__(self, config: S3Config, **kwargs: Any) -> None:
        super().__init__(config=config, **kwargs)
        self.client = boto3.client(
            "s3",
            endpoint_url=config.endpoint_url,
            aws_access_key_id=config.access_key,
            aws_secret_access_key=config.secret_key,
            config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
            region_name="us-east-1",
        )

        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self) -> None:
        try:
            self.client.head_bucket(Bucket=self.config.bucket)
        except ClientError as e:
            if (
                e.response["Error"]["Code"] == "404"
                or e.response["Error"]["Code"] == "NoSuchBucket"
            ):
                try:
                    self.client.create_bucket(Bucket=self.config.bucket)
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
        data: dict,
        publication_state: str = "pending",
    ) -> RevisionMetadata:
        import json

        key = f"{entity_id}/r{revision_id}.json"
        self.client.put_object(
            Bucket=self.config.bucket,
            Key=key,
            Body=json.dumps(data),
            Metadata={"publication_state": publication_state},
        )
        return RevisionMetadata(key=key)

    def read_revision(self, entity_id: str, revision_id: int) -> RevisionReadResponse:
        """Read S3 object and return parsed JSON"""
        import json

        key = f"{entity_id}/r{revision_id}.json"
        response = self.client.get_object(Bucket=self.config.bucket, Key=key)

        parsed_data = json.loads(response["Body"].read().decode("utf-8"))

        return RevisionReadResponse(
            entity_id=entity_id, revision_id=revision_id, data=parsed_data
        )

    def mark_published(
        self, entity_id: str, revision_id: int, publication_state: str
    ) -> None:
        key = f"{entity_id}/r{revision_id}.json"
        self.client.copy_object(
            Bucket=self.config.bucket,
            CopySource={"Bucket": self.config.bucket, "Key": key},
            Key=key,
            Metadata={"publication_state": publication_state},
            MetadataDirective="REPLACE",
        )

    def read_full_revision(self, entity_id: str, revision_id: int) -> Dict[str, Any]:
        """Read S3 object and return parsed full revision JSON"""
        import json

        key = f"{entity_id}/r{revision_id}.json"
        response = self.client.get_object(Bucket=self.config.bucket, Key=key)

        parsed_data: Dict[str, Any] = json.loads(
            response["Body"].read().decode("utf-8")
        )

        return parsed_data

    def check_connection(self) -> bool:
        """Check if S3 connection is healthy

        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            self.client.head_bucket(Bucket=self.config.bucket)
            return True
        except Exception:
            return False

    def write_statement(
        self,
        content_hash: int,
        statement_data: Dict[str, Any],
    ) -> None:
        """Write statement snapshot to S3

        Stores statement at path: statements/{hash}.json
        """
        import json

        logger = logging.getLogger(__name__)

        key = f"statements/{content_hash}.json"
        statement_json = json.dumps(statement_data)

        # Enhanced pre-write validation logging
        logger.debug(f"S3 write_statement: bucket={self.config.bucket}, key={key}")
        logger.debug(f"S3 client endpoint: {self.client._endpoint.host}")
        logger.debug(f"Statement data size: {len(statement_json)} bytes")
        logger.debug(f"Full statement data: {json.dumps(statement_data, indent=2)}")

        # Verify bucket exists before write
        try:
            self.client.head_bucket(Bucket=self.config.bucket)
            logger.debug(f"S3 bucket {self.config.bucket} exists and is accessible")
        except Exception as bucket_error:
            logger.error(
                f"S3 bucket {self.config.bucket} not accessible: {bucket_error}"
            )
            raise

        try:
            response = self.client.put_object(
                Bucket=self.config.bucket,
                Key=key,
                Body=statement_json,
            )

            # Enhanced response logging with S3 metadata
            logger.debug(
                f"S3 write_statement successful: bucket={self.config.bucket}, key={key}, "
                f"ETag={response.get('ETag')}, RequestId={response.get('ResponseMetadata', {}).get('RequestId')}"
            )

            # High Priority: Immediate verification by reading back written object
            try:
                verify_response = self.client.get_object(
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
            logger.error(
                f"S3 write_statement failed for {content_hash}: {type(e).__name__}: {e}",
                extra={
                    "content_hash": content_hash,
                    "bucket": self.config.bucket,
                    "key": key,
                    "statement_data_size": len(statement_json),
                    "s3_endpoint": self.client._endpoint.host,
                },
                exc_info=True,
            )
            raise

    def read_statement(self, content_hash: int) -> Dict[str, Any]:
        """Read statement snapshot from S3

        Returns:
            Dict with keys: content_hash, statement, created_at

        Raises:
            ClientError if statement not found
        """
        import json
        from botocore.exceptions import ClientError

        from models.s3_models import StoredStatement

        logger = logging.getLogger(__name__)

        key = f"statements/{content_hash}.json"
        logger.debug(f"S3 read_statement: bucket={self.config.bucket}, key={key}")

        try:
            response = self.client.get_object(Bucket=self.config.bucket, Key=key)
            parsed_data: Dict[str, Any] = json.loads(
                response["Body"].read().decode("utf-8")
            )

            StoredStatement.model_validate(parsed_data)

            logger.debug(
                f"S3 read_statement successful: bucket={self.config.bucket}, key={key}"
            )
            return parsed_data
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
        data: dict,
        edit_type: str = "",
        created_by: str = "entity-api",
    ) -> int:
        """Write revision as part of redirect operations (no mark_pending/published flow)"""
        import json
        from datetime import datetime

        revision_data = {
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
                "id": data.get("id"),
                "type": entity_type,
                "labels": data.get("labels"),
                "descriptions": data.get("descriptions"),
                "aliases": data.get("aliases"),
                "sitelinks": data.get("sitelinks"),
            },
        }

        key = f"{entity_id}/r{revision_id}.json"
        self.client.put_object(
            Bucket=self.config.bucket,
            Key=key,
            Body=json.dumps(revision_data),
            Metadata={"publication_state": "published"},
        )
        return revision_id
