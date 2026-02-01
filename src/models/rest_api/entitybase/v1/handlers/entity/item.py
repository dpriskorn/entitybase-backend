"""Item-specific entity handlers."""

import logging
import traceback
from datetime import datetime
from typing import Any

from models.data.infrastructure.s3.enums import EntityType
from models.data.infrastructure.stream.change_type import ChangeType
from models.data.rest_api.v1.entitybase.request import EntityCreateRequest
from models.data.rest_api.v1.entitybase.request.entity import PreparedRequestData
from models.data.rest_api.v1.entitybase.request.entity.revision import CreateRevisionRequest
from models.data.rest_api.v1.entitybase.response import EntityResponse
from models.common import EditHeaders
from models.rest_api.utils import raise_validation_error
from .create import EntityCreateHandler
from .creation_transaction import CreationTransaction

logger = logging.getLogger(__name__)


class ItemCreateHandler(EntityCreateHandler):
    """Handler for item creation operations"""

    def _resolve_entity_id(self, request: EntityCreateRequest) -> str:
        """Resolve or auto-assign entity ID."""
        entity_id = request.id
        if entity_id:
            exists = self.state.vitess_client.id_resolver.entity_exists(entity_id)
            logger.debug(f"🔍 HANDLER: Entity exists check: {exists}")
            if exists:
                logger.error(f"🔍 HANDLER: Entity {entity_id} already exists")
                raise_validation_error("Entity already exists", status_code=409)
        else:
            logger.info("🔍 HANDLER: Auto-assigning entity ID")
            if self.enumeration_service is None:
                logger.error("🔍 HANDLER: Enumeration service not available")
                raise_validation_error(
                    "Enumeration service not available", status_code=500
                )
            assert self.enumeration_service is not None
            entity_id = self.enumeration_service.get_next_entity_id("item")
            logger.info(f"🔍 HANDLER: Auto-assigned entity_id: {entity_id}")
        request.id = entity_id
        return entity_id

    @staticmethod
    def _prepare_request_data(request: EntityCreateRequest, entity_id: str) -> PreparedRequestData:
        """Prepare request data for entity creation."""
        request_data_dict = request.data.copy()
        request_data_dict["id"] = entity_id
        logger.debug(f"🔍 HANDLER: Prepared request data: {request_data_dict}")
        return PreparedRequestData(**request_data_dict)

    @staticmethod
    def _create_revision_request(
            entity_id: str,
        request_data: dict[str, Any],
        request: EntityCreateRequest,
        edit_headers: EditHeaders,
        hash_result,
    ) -> CreateRevisionRequest:
        """Create revision request object."""
        return CreateRevisionRequest(
            entity_id=entity_id,
            new_revision_id=1,
            head_revision_id=0,
            request_data=request_data,
            entity_type=EntityType.ITEM,
            hash_result=hash_result,
            is_mass_edit=request.is_mass_edit,
            edit_type=request.edit_type,
            edit_summary=edit_headers.x_edit_summary,
            is_semi_protected=request.state.is_semi_protected,
            is_locked=request.state.is_locked,
            is_archived=request.state.is_archived,
            is_dangling=request.state.is_dangling,
            is_mass_edit_protected=request.state.is_mass_edit_protected,
            is_creation=True,
            user_id=edit_headers.x_user_id,
        )

    async def _execute_creation_transaction(
        self,
        tx: CreationTransaction,
        entity_id: str,
        request_data: PreparedRequestData,
        request: EntityCreateRequest,
        edit_headers: EditHeaders,
        validator: Any,
    ) -> EntityResponse:
        """Execute the creation transaction operations."""
        tx.register_entity(entity_id)
        logger.debug(f"🔍 HANDLER: Entity {entity_id} registered successfully")

        hash_result = tx.process_statements(entity_id, request_data, validator)
        logger.debug(f"🔍 HANDLER: Statements processed, hash_result: {hash_result}")

        revision_request = self._create_revision_request(
            entity_id, request_data, request, edit_headers, hash_result
        )
        response = await tx.create_revision(revision_request)
        logger.debug(f"🔍 HANDLER: Revision created: {response}")

        tx.publish_event(
            entity_id=entity_id,
            revision_id=1,
            change_type=ChangeType.CREATION,
            edit_headers=edit_headers,
            changed_at=datetime.now(),
        )
        logger.debug("🔍 HANDLER: Event published successfully")

        tx.commit()
        logger.debug("🔍 HANDLER: Transaction committed successfully")

        return response  # type: ignore[no-any-return]

    async def create_entity(
        self,
        request: EntityCreateRequest,
        edit_headers: EditHeaders,
        validator: Any | None = None,
        auto_assign_id: bool = False,
    ) -> EntityResponse:
        """Create a new item with auto-assigned Q ID using EntityTransaction."""
        logger.info(f"🔍 HANDLER: Starting item creation for {request.id or 'auto-assign'}")
        logger.debug(f"🔍 HANDLER: Request: {request.model_dump()}")
        entity_id = self._resolve_entity_id(request)

        logger.info("🔍 HANDLER: Preparing request data")
        request_data = self._prepare_request_data(request, entity_id)

        logger.info("🔍 HANDLER: Creating transaction")
        tx = CreationTransaction(state=self.state)
        logger.debug("🔍 HANDLER: Transaction created successfully")
        try:
            response = await self._execute_creation_transaction(
                tx, entity_id, request_data, request, edit_headers, validator
            )

            if self.enumeration_service:
                assert self.enumeration_service is not None
                self.enumeration_service.confirm_id_usage(entity_id)

            logger.info(f"Item creation successful for {entity_id}")
            return response
        except Exception as e:
            logger.error(
                f"Item creation failed for {entity_id}: {e}\n{traceback.format_exc()}"
            )
            tx.rollback()
            raise
