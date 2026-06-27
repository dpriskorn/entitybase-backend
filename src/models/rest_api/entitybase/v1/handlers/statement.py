"""Statement management handlers."""

import logging

from botocore.exceptions import ClientError  # type: ignore[import-untyped]
from typing import Any, cast

from models.data.infrastructure.s3.statement import StatementData
from models.rest_api.entitybase.v1.handler import Handler
from models.data.rest_api.v1.entitybase.request import CleanupOrphanedRequest
from models.data.rest_api.v1.entitybase.request import StatementBatchRequest
from models.data.rest_api.v1.entitybase.response import CleanupOrphanedResponse
from models.data.rest_api.v1.entitybase.response import (
    MostUsedStatementsResponse,
    PropertyCountsResponse,
    PropertyHashesResponse,
    PropertyListResponse,
    StatementBatchResponse,
    StatementResponse,
)
from models.rest_api.entitybase.v1.services.snak_handler import SnakHandler
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)


class StatementHandler(Handler):
    """Handles all statement operations."""

    def _reconstruct_mainsnak(
        self,
        statement_dict: dict[str, Any],
        snak_handler: SnakHandler,
        content_hash: int,
    ) -> StatementData:
        """Reconstruct mainsnak from hash reference in statement.

        Args:
            statement_dict: Statement dictionary with mainsnak hash reference
            snak_handler: Handler for retrieving snaks
            content_hash: Statement content hash for logging

        Returns:
            Statement data with reconstructed mainsnak
        """
        mainsnak_hash = self._extract_mainsnak_hash(statement_dict["mainsnak"])

        retrieved_snak = snak_handler.get_snak(mainsnak_hash)
        if retrieved_snak:
            statement_dict["mainsnak"] = retrieved_snak
            logger.debug(
                f"Reconstructed mainsnak {mainsnak_hash} for statement {content_hash}"
            )
        else:
            logger.warning(
                f"Snak {mainsnak_hash} not found for statement {content_hash}"
            )
        return StatementData(**statement_dict)

    def _extract_mainsnak_hash(self, mainsnak_input: Any) -> int:
        """Extract mainsnak hash from statement mainsnak field.

        Args:
            mainsnak_input: The mainsnak value from statement (either a hash int
                or a dict with a 'hash' key)

        Returns:
            The mainsnak hash as int
        """
        if isinstance(mainsnak_input, dict) and "hash" in mainsnak_input:
            return cast(int, mainsnak_input["hash"])
        return cast(int, mainsnak_input)

    def get_statement(self, content_hash: int) -> StatementResponse:
        """Get a single statement by its hash.

        Returns the full statement JSON from S3.
        """
        logger.debug(f"Getting statement {content_hash}")

        if self.state.s3_client is None:
            logger.error("S3 client is None - not initialized")
            raise_validation_error("S3 not initialized", status_code=503)

        logger.debug(
            f"S3 client initialized, attempting to read statement {content_hash}"
        )

        try:
            statement_data = self.state.s3_client.read_statement(content_hash)
            logger.debug(f"Successfully retrieved statement {content_hash} from S3")

            snak_handler = SnakHandler(state=self.state)
            statement_dict = self._reconstruct_mainsnak(
                statement_data.statement.copy(), snak_handler, content_hash
            )

            return StatementResponse(  # type: ignore[call-arg]
                schema=statement_data.schema_version,
                hash=content_hash,
                statement=statement_dict,
                created_at=statement_data.created_at,
            )
        except Exception as e:
            logger.error(
                f"Failed to retrieve statement {content_hash} from S3",
                extra={
                    "content_hash": content_hash,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "s3_client_initialized": self.state.s3_client is not None,
                },
            )
            raise_validation_error(
                f"Statement {content_hash} not found", status_code=404
            )

    def get_statements_batch(self, hashes: list[int]) -> list[StatementResponse | None]:
        """Get multiple statements by their hashes.

        Efficiently fetches multiple statements in one request.
        Returns array with null for any hashes that don't exist.
        """
        logger.debug(f"[STMT_GET_BATCH] Requested hashes: {hashes}")

        if self.state.s3_client is None:
            logger.error("[STMT_GET_BATCH] S3 client is None")
            if hashes:
                raise_validation_error(
                    f"Statement {hashes[0]} not found", status_code=404
                )
            return []

        # Initialize SnakHandler for batch processing
        snak_handler = SnakHandler(state=self.state)

        statements: list[StatementResponse | None] = []

        for content_hash in hashes:
            logger.debug(f"[STMT_GET_BATCH] Processing hash: {content_hash}")
            try:
                statement_data = self.state.s3_client.read_statement(content_hash)
                logger.debug(
                    f"[STMT_GET_BATCH] Successfully loaded statement: hash={content_hash}"
                )

                statement_dict = self._reconstruct_mainsnak(
                    statement_data.statement.copy(), snak_handler, content_hash
                )

                statements.append(
                    StatementResponse(  # type: ignore[call-arg]
                        schema=statement_data.schema_version,
                        hash=content_hash,
                        statement=statement_dict,
                        created_at=statement_data.created_at,
                    )
                )
            except (ClientError, Exception) as e:
                logger.warning(
                    f"[STMT_GET_BATCH] Failed to load statement hash={content_hash}: "
                    f"error={type(e).__name__}: {e}"
                )
                statements.append(None)

        null_count = sum(1 for s in statements if s is None)
        logger.debug(
            f"[STMT_GET_BATCH] Completed: requested={len(hashes)}, "
            f"found={len(statements) - null_count}, nulls={null_count}"
        )
        return statements

    def get_entity_properties(self, entity_id: str) -> PropertyListResponse:
        """Get list of unique property IDs for an entity's head revision.

        Returns sorted list of properties used in entity statements.
        """
        if self.state.vitess_client is None:
            raise_validation_error("database not initialized", status_code=503)

        if not self.state.vitess_client.entity_exists(entity_id):
            raise_validation_error("Entity not found", status_code=404)

        head_revision_id = self.state.vitess_client.get_head(entity_id)
        if head_revision_id == 0:
            raise_validation_error("Entity has no revisions", status_code=404)

        history = self.state.vitess_client.get_history(entity_id)
        revision_record = next(
            (r for r in history if r.revision_id == head_revision_id), None
        )

        if not revision_record:
            raise_validation_error(
                "Head revision not found in history", status_code=404
            )

        revision_metadata = self.state.s3_client.read_full_revision(
            entity_id, head_revision_id
        )
        properties = revision_metadata.revision.get("properties", [])  # type: ignore[attr-defined]
        return PropertyListResponse(properties=properties)

    def get_entity_property_counts(self, entity_id: str) -> PropertyCountsResponse:
        """Get statement counts per property for an entity's head revision.

        Returns dict mapping property ID -> count of statements.
        """
        if self.state.vitess_client is None:
            raise_validation_error("database not initialized", status_code=503)

        if not self.state.vitess_client.entity_exists(entity_id):
            raise_validation_error("Entity not found", status_code=404)

        head_revision_id = self.state.vitess_client.get_head(entity_id)
        if head_revision_id == 0:
            raise_validation_error("Entity has no revisions", status_code=404)

        revision_metadata = self.state.s3_client.read_full_revision(
            entity_id, head_revision_id
        )
        property_counts = revision_metadata.revision.get("property_counts", {})  # type: ignore[attr-defined]
        return PropertyCountsResponse(property_counts=property_counts)

    def get_entity_property_hashes(
        self,
        entity_id: str,
        property_list: str,
    ) -> PropertyHashesResponse:
        """Get statement hashes for specific properties.

        Property list format: comma-separated property IDs (e.g., P31,P569)

        Returns list of statement hashes for specified properties.
        Uses schema 1.2.0 architecture where statements are stored separately by hash.
        """
        logger.debug(f"get_entity_property_hashes called for entity {entity_id}")
        self._validate_entity_access(entity_id)

        head_revision_id = self.state.vitess_client.get_head(entity_id)
        revision_metadata = self.state.s3_client.read_full_revision(
            entity_id, head_revision_id
        )

        requested_property_ids = [
            p.strip() for p in property_list.split(",") if p.strip()
        ]
        statement_hashes = revision_metadata.revision.get("statements", [])

        matching_hashes = self._filter_statements_by_property(
            statement_hashes, requested_property_ids
        )

        return PropertyHashesResponse(property_hashes=matching_hashes)

    def _validate_entity_access(self, entity_id: str) -> None:
        """Validate entity exists and is accessible."""
        if self.state.vitess_client is None:
            raise_validation_error("database not initialized", status_code=503)

        if not self.state.vitess_client.entity_exists(entity_id):
            raise_validation_error("Entity not found", status_code=404)

        head_revision_id = self.state.vitess_client.get_head(entity_id)
        if head_revision_id == 0:
            raise_validation_error("Entity has no revisions", status_code=404)

    def _filter_statements_by_property(
        self, statement_hashes: list, requested_property_ids: list[str]
    ) -> list[int]:
        """Filter statement hashes by requested property IDs."""
        matching_hashes = []
        snak_handler = SnakHandler(state=self.state)

        for statement_hash in statement_hashes:
            try:
                property_id = self._get_statement_property(statement_hash, snak_handler)
                if property_id and property_id in requested_property_ids:
                    matching_hashes.append(statement_hash)
            except Exception as e:
                raise_validation_error(
                    f"Failed to read statement {statement_hash}: {e}", status_code=500
                )

        return matching_hashes

    def _get_statement_property(
        self, statement_hash: int, snak_handler: SnakHandler
    ) -> str | None:
        """Get property ID for a statement."""
        statement_data = self.state.s3_client.read_statement(statement_hash)

        mainsnak_hash = self._extract_mainsnak_hash(
            statement_data.statement["mainsnak"]
        )

        retrieved_snak = snak_handler.get_snak(mainsnak_hash)
        if retrieved_snak:
            return retrieved_snak.property  # type: ignore[no-any-return]
        else:
            logger.warning(
                f"Snak {mainsnak_hash} not found for statement {statement_hash}"
            )
            return None

    def get_most_used_statements(
        self,
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
            raise_validation_error("database not initialized", status_code=503)

        statement_hashes = self.state.vitess_client.statement_repository.get_most_used(
            limit=limit, min_ref_count=min_ref_count
        )
        return MostUsedStatementsResponse(statements=statement_hashes)

    def cleanup_orphaned_statements(
        self,
        request: CleanupOrphanedRequest,
    ) -> CleanupOrphanedResponse:
        """Clean up orphaned statements that are no longer referenced.

        Removes statements with ref_count <= 0 that are older than the specified days.
        Limited to the specified number to avoid long-running operations.
        """
        if self.state.vitess_client is None:
            raise_validation_error("database not initialized", status_code=503)

        if self.state.s3_client is None:
            raise_validation_error("S3 not initialized", status_code=503)

        # Get orphaned statements older than specified days
        orphaned_hashes = self.state.vitess_client.get_orphaned_statements(
            request.older_than_days, request.limit
        )

        cleaned_count = 0
        failed_count = 0
        errors = []

        for statement_hash in orphaned_hashes:
            try:
                # Delete from S3 first
                self.state.s3_client.delete_statement(statement_hash)
                # Then delete from database
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
