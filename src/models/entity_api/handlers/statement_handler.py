import json
import logging
from typing import Any

from fastapi import HTTPException
from rapidhash import rapidhash

from models.entity import (
    MostUsedStatementsResponse,
    PropertyCountsResponse,
    PropertyHashesResponse,
    PropertyListResponse,
    StatementBatchRequest,
    StatementBatchResponse,
    StatementResponse,
)
from models.infrastructure.s3_client import S3Client
from models.infrastructure.vitess_client import VitessClient

logger = logging.getLogger(__name__)


class StatementHandler:
    """Handles all statement operations."""

    def get_statement(self, content_hash: int, s3_client: S3Client) -> StatementResponse:
        """Get a single statement by its hash.

        Returns the full statement JSON from S3.
        """
        logger.debug(f"Getting statement {content_hash}")

        if s3_client is None:
            logger.error("S3 client is None - not initialized")
            raise HTTPException(status_code=503, detail="S3 not initialized")

        logger.debug(f"S3 client initialized, attempting to read statement {content_hash}")

        try:
            statement_data = s3_client.read_statement(content_hash)
            logger.debug(f"Successfully retrieved statement {content_hash} from S3")
            return StatementResponse(
                content_hash=content_hash,
                statement=statement_data["statement"],
                created_at=statement_data["created_at"],
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
            raise HTTPException(
                status_code=404, detail=f"Statement {content_hash} not found"
            )

    def get_statements_batch(
        self, request: StatementBatchRequest, s3_client: S3Client
    ) -> StatementBatchResponse:
        """Get multiple statements by their hashes.

        Efficiently fetches multiple statements in one request.
        Returns not_found list for any hashes that don't exist.
        """
        if s3_client is None:
            raise HTTPException(status_code=503, detail="S3 not initialized")

        statements = []
        not_found = []

        for content_hash in request.hashes:
            try:
                statement_data = s3_client.read_statement(content_hash)
                statements.append(
                    StatementResponse(
                        content_hash=content_hash,
                        statement=statement_data["statement"],
                        created_at=statement_data["created_at"],
                    )
                )
            except Exception:
                not_found.append(content_hash)

        return StatementBatchResponse(statements=statements, not_found=not_found)

    def get_entity_properties(
        self, entity_id: str, vitess_client: VitessClient, s3_client: S3Client
    ) -> PropertyListResponse:
        """Get list of unique property IDs for an entity's head revision.

        Returns sorted list of properties used in entity statements.
        """
        if vitess_client is None:
            raise HTTPException(status_code=503, detail="Vitess not initialized")

        if not vitess_client.entity_exists(entity_id):
            raise HTTPException(status_code=404, detail="Entity not found")

        head_revision_id = vitess_client.get_head(entity_id)
        if head_revision_id == 0:
            raise HTTPException(status_code=404, detail="Entity has no revisions")

        history = vitess_client.get_history(entity_id)
        revision_record = next(
            (r for r in history if r.revision_id == head_revision_id), None
        )

        if not revision_record:
            raise HTTPException(
                status_code=404, detail="Head revision not found in history"
            )

        revision_metadata = s3_client.read_full_revision(entity_id, head_revision_id)
        properties = revision_metadata.get("properties", [])
        return PropertyListResponse(properties=properties)

    def get_entity_property_counts(
        self, entity_id: str, vitess_client: VitessClient, s3_client: S3Client
    ) -> PropertyCountsResponse:
        """Get statement counts per property for an entity's head revision.

        Returns dict mapping property ID -> count of statements.
        """
        if vitess_client is None:
            raise HTTPException(status_code=503, detail="Vitess not initialized")

        if not vitess_client.entity_exists(entity_id):
            raise HTTPException(status_code=404, detail="Entity not found")

        head_revision_id = vitess_client.get_head(entity_id)
        if head_revision_id == 0:
            raise HTTPException(status_code=404, detail="Entity has no revisions")

        revision_metadata = s3_client.read_full_revision(entity_id, head_revision_id)
        property_counts = revision_metadata.get("property_counts", {})
        return PropertyCountsResponse(property_counts=property_counts)

    def get_entity_property_hashes(
        self,
        entity_id: str,
        property_list: str,
        vitess_client: VitessClient,
        s3_client: S3Client,
    ) -> PropertyHashesResponse:
        """Get statement hashes for specific properties.

        Property list format: comma-separated property IDs (e.g., P31,P569)

        Returns list of statement hashes for the specified properties.
        """
        if vitess_client is None:
            raise HTTPException(status_code=503, detail="Vitess not initialized")

        if not vitess_client.entity_exists(entity_id):
            raise HTTPException(status_code=404, detail="Entity not found")

        head_revision_id = vitess_client.get_head(entity_id)
        if head_revision_id == 0:
            raise HTTPException(status_code=404, detail="Entity has no revisions")

        revision_metadata = s3_client.read_full_revision(entity_id, head_revision_id)

        property_ids = [p.strip() for p in property_list.split(",") if p.strip()]

        all_properties = revision_metadata.get("properties", [])

        property_hash_map: dict[Any, Any] = {}
        entity_data = s3_client.read_revision(entity_id, head_revision_id)
        claims = entity_data.data.get("entity", {}).get("claims", {})

        for prop_id in property_ids:
            if prop_id not in all_properties:
                continue
            claim_list = claims.get(prop_id, [])
            for claim in claim_list:
                try:
                    claim_json = json.dumps(claim, sort_keys=True)
                    claim_hash = rapidhash(claim_json.encode())
                    property_hash_map.setdefault(prop_id, []).append(claim_hash)
                except Exception as e:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to hash claim: {e}",
                    )

        flat_hashes = []
        for prop_id in property_ids:
            if prop_id in property_hash_map:
                flat_hashes.extend(property_hash_map[prop_id])

        return PropertyHashesResponse(property_hashes=flat_hashes)

    def get_most_used_statements(
        self,
        vitess_client: VitessClient,
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
        if vitess_client is None:
            raise HTTPException(status_code=503, detail="Vitess not initialized")

        try:
            statement_hashes = vitess_client.get_most_used_statements(
                limit=limit, min_ref_count=min_ref_count
            )
            return MostUsedStatementsResponse(statements=statement_hashes)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error fetching most-used statements: {e}"
            )