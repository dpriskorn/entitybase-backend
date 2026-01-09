import logging
from typing import Any

from fastapi import HTTPException

from models.api_models import EntityUpdateRequest, EntityResponse
from models.infrastructure.s3.s3_client import S3Client
from models.infrastructure.stream.producer import StreamProducerClient
from models.infrastructure.vitess_client import VitessClient
from . import EntityHandler

logger = logging.getLogger(__name__)


class EntityUpdateHandler(EntityHandler):
    """Handler for entity update operations"""

    async def update_entity(
        self,
        entity_id: str,
        request: EntityUpdateRequest,
        vitess_client: VitessClient,
        s3_client: S3Client,
        stream_producer: StreamProducerClient | None,
        validator: Any | None = None,
    ) -> EntityResponse:
        """Update an existing entity. Fails if entity doesn't exist."""
        logger.info(
            f"=== ENTITY UPDATE START: {entity_id} ===",
            extra={
                "entity_id": entity_id,
                "entity_type": request.type,
                "is_mass_edit": request.is_mass_edit,
                "edit_type": request.edit_type,
                "data_keys": list(request.data.keys()),
                "has_claims": bool(request.data.get("claims")),
                "operation": "update_entity_start",
            },
        )

        # Check if entity exists - for update, this is required
        entity_existed = vitess_client.entity_exists(entity_id)
        if not entity_existed:
            logger.error(f"Entity {entity_id} does not exist, cannot update")
            raise HTTPException(status_code=404, detail="Entity not found")

        # Check deletion status
        is_deleted = vitess_client.is_entity_deleted(entity_id)
        if is_deleted:
            raise HTTPException(
                status_code=410, detail=f"Entity {entity_id} has been deleted"
            )

        # Add entity_id to request data for consistency
        request_data = request.data
        request_data["id"] = entity_id

        # Common processing logic
        return await self._process_entity_revision(
            entity_id=entity_id,
            request_data=request_data,
            entity_type=request.type,
            is_mass_edit=request.is_mass_edit,
            edit_type=request.edit_type,
            edit_summary=request.edit_summary,
            editor=request.editor,
            is_semi_protected=request.is_semi_protected,
            is_locked=request.is_locked,
            is_archived=request.is_archived,
            is_dangling=request.is_dangling,
            is_mass_edit_protected=request.is_mass_edit_protected,
            is_not_autoconfirmed_user=request.is_not_autoconfirmed_user,
            vitess_client=vitess_client,
            s3_client=s3_client,
            stream_producer=stream_producer,
            validator=validator,
            is_creation=False,
        )
