"""Entity creation handlers."""

import logging
from typing import Any

from pydantic import ConfigDict, Field

from ...request.enums import UserActivityType

logger = logging.getLogger(__name__)

from models.rest_api.utils import raise_validation_error
from models.infrastructure.s3.s3_client import MyS3Client
from models.infrastructure.stream.producer import StreamProducerClient
from models.infrastructure.vitess.vitess_client import VitessClient
from .base import EntityHandler
from models.rest_api.entitybase.request import EntityCreateRequest
from models.rest_api.entitybase.response import EntityResponse
from models.rest_api.entitybase.services.enumeration_service import EnumerationService

logger = logging.getLogger(__name__)


class EntityCreateHandler(EntityHandler):
    """Handler for entity creation operations"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    enumeration_service: EnumerationService | None = Field(default=None)

    def __init__(
        self, /, enumeration_service: EnumerationService | None = None, **data: Any
    ):
        super().__init__(**data)
        self.enumeration_service = enumeration_service

    async def create_entity(
        self,
        request: EntityCreateRequest,
        vitess_client: VitessClient,
        s3_client: MyS3Client,
        stream_producer: StreamProducerClient | None,
        validator: Any | None = None,
        auto_assign_id: bool = False,
        user_id: int = 0,
    ) -> EntityResponse:
        """Create a new entity. Fails if entity already exists."""
        # Auto-assign ID if requested (for type-specific endpoints)
        if auto_assign_id:
            if self.enumeration_service is None:
                raise_validation_error(
                    "Enumeration service not available", status_code=500
                )
            assert self.enumeration_service is not None
            entity_id = self.enumeration_service.get_next_entity_id(request.type)
            request.id = entity_id
            # Add ID to request data
            request_data = request.data.copy()
            request_data["id"] = entity_id
        else:
            if request.id is None:
                raise_validation_error(
                    "id is required for entity creation", status_code=400
                )
            assert request.id is not None
            entity_id = request.id
            request_data = request.data

        logger.info(
            f"=== ENTITY CREATION START: {entity_id} ===",
            extra={
                "entity_id": entity_id,
                "entity_type": request.type,
                "is_mass_edit": request.is_mass_edit,
                "edit_type": request.edit_type,
                "data_keys": list(request_data.keys()),
                "has_claims": bool(request_data.get("claims")),
                "operation": "create_entity_start",
            },
        )

        # Check if entity already exists - for create, this should fail
        entity_existed = vitess_client.entity_exists(entity_id)
        if entity_existed:
            logger.error(f"Entity {entity_id} already exists, cannot create")
            raise_validation_error("Entity already exists", status_code=409)

        # Register the new entity
        vitess_client.register_entity(entity_id)

        # Check deletion status
        is_deleted = vitess_client.is_entity_deleted(entity_id)
        if is_deleted:
            raise_validation_error(
                f"Entity {entity_id} has been deleted", status_code=410
            )

        # Common processing logic using new architecture
        from models.infrastructure.s3.enums import EntityType
        response = await self.process_entity_revision_new(
            entity_id=entity_id,
            request_data=request_data,
            entity_type=EntityType(request.type),
            edit_type=request.edit_type,
            edit_summary=request.edit_summary,
            is_creation=True,
            vitess_client=vitess_client,
            s3_client=s3_client,
            stream_producer=stream_producer,
            validator=validator,
        )

        # Log activity
        if user_id > 0:
            activity_result = vitess_client.user_repository.log_user_activity(
                user_id=user_id,
                activity_type=UserActivityType.ENTITY_CREATE,
                entity_id=entity_id,
                revision_id=response.revision_id,
            )
            if not activity_result.success:
                logger.warning(f"Failed to log user activity: {activity_result.error}")

        return response  # type: ignore[no-any-return]
