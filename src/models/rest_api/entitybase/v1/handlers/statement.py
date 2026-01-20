"""Statement management handlers."""

import logging

from botocore.exceptions import ClientError  # type: ignore[import-untyped]
from typing_extensions import TYPE_CHECKING

from models.rest_api.entitybase.v1.handler import Handler
from models.rest_api.entitybase.v1.request.statement import StatementBatchRequest
from models.rest_api.entitybase.v1.request.misc import CleanupOrphanedRequest
from models.rest_api.entitybase.v1.response import (
    MostUsedStatementsResponse,
    PropertyCountsResponse,
    PropertyHashesResponse,
    PropertyListResponse,
    StatementBatchResponse,
    StatementResponse,
)
from models.rest_api.entitybase.v1.response import CleanupOrphanedResponse
from models.rest_api.utils import raise_validation_error

if TYPE_CHECKING:
    from models.infrastructure.s3.client import MyS3Client
    from models.infrastructure.vitess.client import VitessClient

logger = logging.getLogger(__name__)


class StatementHandler(Handler):
    """Handles all statement operations."""

    def get_statement(
        self, content_hash: int, s3_client: "MyS3Client | None"
    ) -> StatementResponse:
        """Get a single statement by its hash.

        Returns the full statement JSON from S3.
        """
        logger.debug(f"Getting statement {content_hash}")

        if s3_client is None:
            logger.error("S3 client is None - not initialized")
            raise_validation_error("S3 not initialized", status_code=503)

        logger.debug(
            f"S3 client initialized, attempting to read statement {content_hash}"
        )

        try:
            statement_data = s3_client.read_statement(content_hash)
            logger.debug(f"Successfully retrieved statement {content_hash} from S3")
            return StatementResponse(  # type: ignore[call-arg]
                schema=statement_data.schema_version,
                hash=content_hash,
                statement=statement_data.statement,
                created_at=statement_data.created_at,
            )
        except Exception as e:
            logger.error(
                f"Failed to retrieve statement {content_hash} from S3",
                extra={
                    "content_hash": content_hash,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "s3_client_initialized": s3_client is not None,
                },
            )
            raise_validation_error(
                f"Statement {content_hash} not found", status_code=404
            )

    def get_statements_batch(
        self, request: StatementBatchRequest, s3_client: "MyS3Client | None"
    ) -> StatementBatchResponse:
        """Get multiple statements by their hashes.

        Efficiently fetches multiple statements in one request.
        Returns not_found list for any hashes that don't exist.
        """
        if s3_client is None:
            raise_validation_error(
                f"Statement {request.hashes[0]} not found", status_code=404
            )

        statements = []
        not_found = []

        for content_hash in request.hashes:
            try:
                statement_data = s3_client.read_statement(content_hash)
                statements.append(
                    StatementResponse(  # type: ignore[call-arg]
                        schema=statement_data.schema_version,
                        hash=content_hash,
                        statement=statement_data.statement,
                        created_at=statement_data.created_at,
                    )
                )
            except ClientError:
                not_found.append(content_hash)

        return StatementBatchResponse(statements=statements, not_found=not_found)

    def get_entity_properties(
        self, entity_id: str: "VitessClient", s3_client: "MyS3Client"
    ) -> PropertyListResponse:
        """Get list of unique property IDs for an entity's head revision.

        Returns sorted list of properties used in entity statements.
        """
        if self.state.vitess_client is None:
            raise_validation_error("Vitess not initialized", status_code=503)

        if not vitess_client.entity_exists(entity_id):
            raise_validation_error("Entity not found", status_code=404)

        head_revision_id = vitess_client.get_head(entity_id)
        if head_revision_id == 0:
            raise_validation_error("Entity has no revisions", status_code=404)

        history = vitess_client.get_history(entity_id)
        revision_record = next(
            (r for r in history if r.revision_id == head_revision_id), None
        )

        if not revision_record:
            raise_validation_error(
                "Head revision not found in history", status_code=404
            )

        revision_metadata = s3_client.read_full_revision(entity_id, head_revision_id)
        properties = revision_metadata.data.get("properties", [])  # type: ignore[attr-defined]
        return PropertyListResponse(properties=properties)

    def get_entity_property_counts(
        self, entity_id: str: "VitessClient", s3_client: "MyS3Client"
    ) -> PropertyCountsResponse:
        """Get statement counts per property for an entity's head revision.

        Returns dict mapping property ID -> count of statements.
        """
        if self.state.vitess_client is None:
            raise_validation_error("Vitess not initialized", status_code=503)

        if not vitess_client.entity_exists(entity_id):
            raise_validation_error("Entity not found", status_code=404)

        head_revision_id = vitess_client.get_head(entity_id)
        if head_revision_id == 0:
            raise_validation_error("Entity has no revisions", status_code=404)

        revision_metadata = s3_client.read_full_revision(entity_id, head_revision_id)
        property_counts = revision_metadata.data.get("property_counts", {})  # type: ignore[attr-defined]
        return PropertyCountsResponse(property_counts=property_counts)

    def get_entity_property_hashes(
        self,
        entity_id: str,
        property_list: str,
        vitess_client: "VitessClient",
        s3_client: "MyS3Client",
    ) -> PropertyHashesResponse:
        """Get statement hashes for specific properties.

        Property list format: comma-separated property IDs (e.g., P31,P569)

        Returns list of statement hashes for specified properties.
        Uses schema 1.2.0 architecture where statements are stored separately by hash.
        """
        logger.debug(f"get_entity_property_hashes called for entity {entity_id}")
        if self.state.vitess_client is None:
            raise_validation_error("Vitess not initialized", status_code=503)

        if not vitess_client.entity_exists(entity_id):
            raise_validation_error("Entity not found", status_code=404)

        head_revision_id = vitess_client.get_head(entity_id)
        if head_revision_id == 0:
            raise_validation_error("Entity has no revisions", status_code=404)

        revision_metadata = s3_client.read_full_revision(entity_id, head_revision_id)

        requested_property_ids = [
            p.strip() for p in property_list.split(",") if p.strip()
        ]
        statement_hashes = revision_metadata.data.get("statements", [])  # type: ignore[attr-defined]

        matching_hashes = []

        for statement_hash in statement_hashes:
            try:
                statement_data = s3_client.read_statement(statement_hash)

                property_id = statement_data.statement["mainsnak"]["property"]

                if property_id in requested_property_ids:
                    matching_hashes.append(statement_hash)
            except Exception as e:
                raise_validation_error(
                    f"Failed to read statement {statement_hash}: {e}", status_code=500
                )

        return PropertyHashesResponse(property_hashes=matching_hashes)

    def get_most_used_statements(
        self,
        vitess_client: "VitessClient",
        limit: int = 100,
        min_ref_count: int = 1,
    ) -> MostUsedStatementsResponse:
        """Get most referenced statements.

        Returns statement hashes sorted by ref_count DESC.
        Useful for analytics and scientific analysis of statement usage patterns.

        Query params:
        - limit: Maximum number of statements to return (1-10000, default 100)
        - min_ref_count: Minimum ref_count threshold (default 1)
        """
        if self.state.vitess_client is None:
            raise_validation_error("Vitess not initialized", status_code=503)

        statement_hashes = vitess_client.get_most_used_statements(
            limit=limit, min_ref_count=min_ref_count
        )
        return MostUsedStatementsResponse(statements=statement_hashes)

    def cleanup_orphaned_statements(
        self,
        request: CleanupOrphanedRequest,
        vitess_client: "VitessClient",
        s3_client: "MyS3Client",
    ) -> CleanupOrphanedResponse:
        """Clean up orphaned statements that are no longer referenced.

        Removes statements with ref_count <= 0 that are older than the specified days.
        Limited to the specified number to avoid long-running operations.
        """
        if self.state.vitess_client is None:
            raise_validation_error("Vitess not initialized", status_code=503)

        if s3_client is None:
            raise_validation_error("S3 not initialized", status_code=503)

        # Get orphaned statements older than specified days
        orphaned_hashes = vitess_client.get_orphaned_statements(
            request.older_than_days, request.limit
        )

        cleaned_count = 0
        failed_count = 0
        errors = []

        for statement_hash in orphaned_hashes:
            try:
                # Delete from S3 first
                s3_client.delete_statement(statement_hash)
                # Then delete from Vitess
                self.state.vitess_client.delete_statement(statement_hash)
                cleaned_count += 1
                logger.info(f"Cleaned up orphaned statement {statement_hash}")
            except Exception as e:
                failed_count += 1
                error_msg = f"Failed to cleanup statement {statement_hash}: {e}"
                errors.append(error_msg)
                logger.error(error_msg)

        return CleanupOrphanedResponse(
            cleaned_count=cleaned_count,
            failed_count=failed_count,
            errors=errors,
        )
