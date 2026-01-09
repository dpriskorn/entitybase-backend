from typing import Any, Dict

from fastapi import HTTPException

from models.api_models import EntityResponse
from models.infrastructure.s3.s3_client import S3Client
from models.infrastructure.vitess_client import VitessClient

import logging

logger = logging.getLogger(__name__)


class EntityReadHandler:
    """Handler for entity read operations"""

    @staticmethod
    def get_entity(
        entity_id: str,
        vitess_client: VitessClient,
        s3_client: S3Client,
    ) -> EntityResponse:
        """Get entity by ID."""
        if vitess_client is None:
            raise HTTPException(status_code=503, detail="Vitess not initialized")

        if s3_client is None:
            raise HTTPException(status_code=503, detail="S3 not initialized")

        if not vitess_client.entity_exists(entity_id):
            raise HTTPException(status_code=404, detail="Entity not found")

        head_revision_id = vitess_client.get_head(entity_id)
        if head_revision_id == 0:
            raise HTTPException(status_code=404, detail="Entity not found")

        try:
            revision = s3_client.read_revision(entity_id, head_revision_id)
            return EntityResponse(
                id=entity_id,
                revision_id=head_revision_id,
                data=revision.data.get("entity", {}),
                is_semi_protected=revision.data.get("is_semi_protected", False),
                is_locked=revision.data.get("is_locked", False),
                is_archived=revision.data.get("is_archived", False),
                is_dangling=revision.data.get("is_dangling", False),
                is_mass_edit_protected=revision.data.get(
                    "is_mass_edit_protected", False
                ),
            )
        except Exception as e:
            logger.error(f"Failed to read entity {entity_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to read entity")

    @staticmethod
    def get_entity_history(
        entity_id: str,
        vitess_client: VitessClient,
        s3_client: S3Client,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Dict[str, Any]]:
        """Get entity revision history."""
        if vitess_client is None:
            raise HTTPException(status_code=503, detail="Vitess not initialized")

        if not vitess_client.entity_exists(entity_id):
            raise HTTPException(status_code=404, detail="Entity not found")

        try:
            # For now, return a simple list. In a real implementation,
            # we'd need to get revision IDs from Vitess
            revisions: list[Dict[str, Any]] = []
            # This is a placeholder - actual implementation would query Vitess
            # for revision history
            logger.info(f"Getting history for {entity_id} (placeholder implementation)")
            return revisions
        except Exception as e:
            logger.error(f"Failed to get entity history for {entity_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to get entity history")

    @staticmethod
    def get_entity_revision(
        entity_id: str,
        revision_id: int,
        s3_client: S3Client,
    ) -> Dict[str, Any]:
        """Get specific entity revision."""
        if s3_client is None:
            raise HTTPException(status_code=503, detail="S3 not initialized")

        try:
            revision = s3_client.read_revision(entity_id, revision_id)
            return {
                "entity_id": entity_id,
                "revision_id": revision_id,
                "data": revision.data,
            }
        except Exception as e:
            logger.error(
                f"Failed to read revision {revision_id} for entity {entity_id}: {e}"
            )
            raise HTTPException(status_code=404, detail="Revision not found")
