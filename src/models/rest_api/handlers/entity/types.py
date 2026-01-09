import logging
from typing import Any

from fastapi import HTTPException

from models.api_models import ItemCreateRequest, EntityCreateRequest, EntityResponse
from models.infrastructure.s3.s3_client import S3Client
from models.infrastructure.stream.producer import StreamProducerClient
from models.infrastructure.vitess_client import VitessClient
from models.rest_api.services.enumeration_service import EnumerationService
from . import EntityHandler
from .creation_transaction import CreationTransaction

logger = logging.getLogger(__name__)


class ItemCreateHandler(EntityHandler):
    """Handler for item creation operations"""

    def __init__(self, enumeration_service: EnumerationService):
        self.enumeration_service = enumeration_service

    async def create_item(
        self,
        request: ItemCreateRequest,
        vitess_client: VitessClient,
        s3_client: S3Client,
        stream_producer: StreamProducerClient | None,
        validator: Any | None = None,
    ) -> EntityResponse:
        """Create a new item with auto-assigned Q ID."""
        # Allocate trusted unique ID
        entity_id = self.enumeration_service.get_next_entity_id("item")
        request.id = entity_id

        # Prepare request data
        request_data = request.data.copy()
        request_data["id"] = entity_id

        logger.info(
            f"=== ITEM CREATION START: {entity_id} ===",
            extra={
                "entity_id": entity_id,
                "entity_type": "item",
                "is_mass_edit": request.is_mass_edit,
                "edit_type": request.edit_type,
                "data_keys": list(request_data.keys()),
                "has_claims": bool(request_data.get("claims")),
                "operation": "create_item_start",
            },
        )

        # Use transaction for atomic creation with rollback
        tx = CreationTransaction()
        try:
            tx.register_entity(vitess_client, entity_id)
            hash_result = tx.process_statements(
                entity_id, request_data, vitess_client, s3_client, validator
            )
            response = tx.create_revision(
                entity_id=entity_id,
                new_revision_id=1,  # Direct for creation
                head_revision_id=0,
                request_data=request_data,
                entity_type="item",
                hash_result=hash_result,
                content_hash=0,  # TODO: calculate
                is_mass_edit=request.is_mass_edit,
                edit_type=request.edit_type,
                edit_summary=request.edit_summary,
                editor=request.editor,
                is_semi_protected=request.is_semi_protected,
                is_locked=request.is_locked,
                is_archived=request.is_archived,
                is_dangling=request.is_dangling,
                is_mass_edit_protected=request.is_mass_edit_protected,
                vitess_client=vitess_client,
                stream_producer=stream_producer,
                is_creation=True,
            )
            tx.publish_event(
                entity_id=entity_id,
                revision_id=1,
                change_type="creation",
                from_revision_id=None,
                changed_at=None,  # TODO
                editor=request.editor,
                edit_summary=request.edit_summary,
                stream_producer=stream_producer,
            )
            tx.commit()
            return response
        except Exception as e:
            logger.error(f"Item creation failed for {entity_id}: {e}")
            tx.rollback()
            raise


class PropertyCreateHandler(EntityHandler):
    """Handler for property creation operations"""

    def __init__(self, enumeration_service: EnumerationService):
        self.enumeration_service = enumeration_service

    async def create_property(
        self,
        request: EntityCreateRequest,
        vitess_client: VitessClient,
        s3_client: S3Client,
        stream_producer: StreamProducerClient | None,
        validator: Any | None = None,
    ) -> EntityResponse:
        """Create a new property with auto-assigned P ID."""
        # Auto-assign P ID
        entity_id = self.enumeration_service.get_next_entity_id("property")
        request.id = entity_id

        # Add ID to request data
        request_data = request.data.copy()
        request_data["id"] = entity_id

        logger.info(
            f"=== PROPERTY CREATION START: {entity_id} ===",
            extra={
                "entity_id": entity_id,
                "entity_type": "property",
                "is_mass_edit": request.is_mass_edit,
                "edit_type": request.edit_type,
                "data_keys": list(request_data.keys()),
                "has_claims": bool(request_data.get("claims")),
                "operation": "create_property_start",
            },
        )

        # Check if entity already exists - for create, this should fail
        entity_existed = vitess_client.entity_exists(entity_id)
        if entity_existed:
            logger.error(f"Property {entity_id} already exists, cannot create")
            raise HTTPException(status_code=409, detail="Property already exists")

        # Register the new entity
        vitess_client.register_entity(entity_id)

        # Check deletion status
        is_deleted = vitess_client.is_entity_deleted(entity_id)
        if is_deleted:
            raise HTTPException(
                status_code=410, detail=f"Property {entity_id} has been deleted"
            )

        # Common processing logic
        return await self._process_entity_revision(
            entity_id=entity_id,
            request_data=request_data,
            entity_type="property",
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
            is_creation=True,
        )
