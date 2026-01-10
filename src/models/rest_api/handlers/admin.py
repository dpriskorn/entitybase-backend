import logging
from typing import Any, Optional

from models.api_models import (
    CleanupOrphanedRequest,
    CleanupOrphanedResponse,
    EntityListResponse,
)
from models.config.settings import raise_validation_error
from models.infrastructure.s3.s3_client import S3Client
from models.infrastructure.vitess_client import VitessClient

logger = logging.getLogger(__name__)


class AdminHandler:
    """Handles administrative operations."""

    @staticmethod
    def cleanup_orphaned_statements(
        request: CleanupOrphanedRequest,
        vitess_client: VitessClient,
        s3_client: S3Client,
    ) -> CleanupOrphanedResponse:
        """Cleanup orphaned statements from S3 and Vitess.

        Orphaned statements are those with ref_count = 0 and are older than
        specified threshold. This endpoint is typically called by a
        background job (e.g., cron) to clean up unused data.

        Query params (in request body):
        - older_than_days: Minimum age in days (default 180)
        - limit: Maximum statements to cleanup (default 1000)

        Returns count of cleaned and failed statements.
        """
        if vitess_client is None:
            raise_validation_error("Vitess not initialized", status_code=503)

        if s3_client is None:
            raise_validation_error("S3 not initialized", status_code=503)

        cleaned_count = 0
        failed_count = 0
        errors = []

        try:
            orphaned_hashes = vitess_client.get_orphaned_statements(
                older_than_days=request.older_than_days, limit=request.limit
            )

            for content_hash in orphaned_hashes:
                try:
                    key = f"statements/{content_hash}.json"
                    s3_client.conn.delete_object(
                        Bucket=s3_client.config.bucket, Key=key
                    )

                    # Use context manager for direct SQL delete
                    with vitess_client.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "DELETE FROM statement_content WHERE content_hash = %s",
                            (content_hash,),
                        )
                        cursor.close()
                    cleaned_count += 1
                except Exception as e:
                    failed_count += 1
                    errors.append(f"Hash {content_hash}: {str(e)}")

            return CleanupOrphanedResponse(
                cleaned_count=cleaned_count,
                failed_count=failed_count,
                errors=errors,
            )
        except Exception as e:
            raise_validation_error(f"Error during orphaned statement cleanup: {e}", status_code=500)

    def list_entities(
        self,
        vitess_client: VitessClient,
        status: Optional[str] = None,
        edit_type: Optional[str] = None,
        limit: int = 100,
    ) -> EntityListResponse:
        """Filter entities by status or edit_type.

        DISABLED: Endpoint not yet implemented
        """
        if vitess_client is None:
            raise_validation_error("Vitess not initialized", status_code=503)

        # Note: Listing methods are disabled until implemented
        entities: list[Any] = []  # Type annotation for linter
        if status == "locked":
            entities = []  # vitess_client.list_locked_entities(limit)
        elif status == "semi_protected":
            entities = []  # vitess_client.list_semi_protected_entities(limit)
        elif status == "archived":
            entities = []  # vitess_client.list_archived_entities(limit)
        elif status == "dangling":
            entities = []  # vitess_client.list_dangling_entities(limit)
        elif edit_type:
            entities = []  # vitess_client.list_by_edit_type(edit_type, limit)
        else:
            raise_validation_error("Must provide status or edit_type filter", status_code=400)

        return EntityListResponse(entities=entities, count=len(entities))

    def get_raw_revision(
        self,
        entity_id: str,
        revision_id: int,
        vitess_client: VitessClient,
        s3_client: S3Client,
    ) -> dict[str, Any]:
        """
        Returns raw S3 entity data for specific revision.

        Pure S3 data - no wrapper, no transformation.

        Returns 404 with typed error_type if:
        - Entity doesn't exist in ID mapping (ENTITY_NOT_FOUND)
        - Entity has no revisions (NO_REVISIONS)
        - Requested revision doesn't exist (REVISION_NOT_FOUND)
        """
        if vitess_client is None:
            raise_validation_error("Vitess not initialized", status_code=503)

        # Check if entity exists and get history
        if not vitess_client.entity_exists(entity_id):
            raise_validation_error(f"Entity {entity_id} not found in ID mapping", status_code=404)

        # Check if revisions exist for entity
        history = vitess_client.get_history(entity_id)
        if not history:
            raise_validation_error(f"Entity {entity_id} has no revisions", status_code=404)

        # Check if requested revision exists
        revision_ids = sorted([r.revision_id for r in history])
        if revision_id not in revision_ids:
            raise_validation_error(
                f"Revision {revision_id} not found for entity {entity_id}. Available revisions: {revision_ids}",
                status_code=404,
            )

        # Read full revision schema from S3
        if s3_client is None:
            raise_validation_error("S3 not initialized", status_code=503)

        revision = s3_client.read_full_revision(entity_id, revision_id)

        # Type assertion to ensure MyPy compatibility
        if not isinstance(revision, dict):
            raise_validation_error(f"Invalid revision data type: expected dict, got {type(revision)}", status_code=500)

        # Return full revision as-is (no transformation)
        return revision
