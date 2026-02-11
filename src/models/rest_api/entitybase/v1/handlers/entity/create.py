"""Entity creation handlers."""

import logging
from typing import Any

from pydantic import ConfigDict, Field

from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from models.data.rest_api.v1.entitybase.request import EntityCreateRequest
from models.data.rest_api.v1.entitybase.response import EntityResponse
from models.rest_api.entitybase.v1.services.enumeration_service import (
    EnumerationService,
)
from models.rest_api.utils import raise_validation_error
from .handler import EntityHandler
from models.data.rest_api.v1.entitybase.request import UserActivityType

logger = logging.getLogger(__name__)


class EntityCreateHandler(EntityHandler):
    """Handler for entity creation operations"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    enumeration_service: EnumerationService | None = Field(default=None)

    async def create_entity(
        self,
        request: EntityCreateRequest,
        edit_headers: EditHeaders,
        validator: Any | None = None,
        auto_assign_id: bool = False,
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
        entity_existed = self.state.vitess_client.entity_exists(entity_id)
        if entity_existed:
            logger.error(f"Entity {entity_id} already exists, cannot create")
            raise_validation_error("Entity already exists", status_code=409)

        # Register the new entity
        self.state.vitess_client.register_entity(entity_id)

        # Check deletion status
        is_deleted = self.state.vitess_client.is_entity_deleted(entity_id)
        if is_deleted:
            raise_validation_error(
                f"Entity {entity_id} has been deleted", status_code=410
            )

        # Common processing logic using new architecture
        from models.data.infrastructure.s3.enums import EntityType
        from models.data.rest_api.v1.entitybase.request.entity.context import (
            ProcessEntityRevisionContext,
        )

        ctx = ProcessEntityRevisionContext(
            entity_id=entity_id,
            request_data=request_data,
            entity_type=EntityType(request.type),
            edit_type=request.edit_type,
            edit_headers=edit_headers,
            is_creation=True,
            validator=validator,
        )
        response = await self.process_entity_revision_new(ctx)

        # Log activity
        if edit_headers.x_user_id > 0:
            activity_result = (
                self.state.vitess_client.user_repository.log_user_activity(
                    user_id=edit_headers.x_user_id,
                    activity_type=UserActivityType.ENTITY_CREATE,
                    entity_id=entity_id,
                    revision_id=response.revision_id,
                )
            )
            if not activity_result.success:
                logger.warning(f"Failed to log user activity: {activity_result.error}")

        return response  # type: ignore[no-any-return]
