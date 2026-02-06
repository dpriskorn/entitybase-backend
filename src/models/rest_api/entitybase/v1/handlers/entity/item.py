"""Item-specific entity handlers."""

import logging
import traceback
from datetime import datetime
from typing import Any

from models.data.infrastructure.s3.enums import EntityType
from models.data.infrastructure.stream.change_type import ChangeType
from models.data.rest_api.v1.entitybase.request import EntityCreateRequest
from models.data.rest_api.v1.entitybase.request.entity import PreparedRequestData
from models.data.rest_api.v1.entitybase.request.entity.context import EditContext, EventPublishContext, CreationTransactionContext
from models.data.rest_api.v1.entitybase.response import EntityResponse
from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
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
    async def _execute_creation_transaction(ctx: CreationTransactionContext) -> EntityResponse:
        """Execute the creation transaction operations."""
        ctx.tx.register_entity(ctx.entity_id)
        logger.debug(f"🔍 HANDLER: Entity {ctx.entity_id} registered successfully")

        hash_result = ctx.tx.process_statements(ctx.entity_id, ctx.request_data, ctx.validator)
        logger.debug(f"🔍 HANDLER: Statements processed, hash_result: {hash_result}")

        response = await ctx.tx.create_revision(
            entity_id=ctx.entity_id,
            request_data=ctx.request_data,
            entity_type=EntityType.ITEM,
            edit_headers=ctx.edit_headers,
            hash_result=hash_result,
        )
        logger.debug(f"🔍 HANDLER: Revision created: {response}")

        edit_context = EditContext(
            user_id=ctx.edit_headers.x_user_id,
            edit_summary=ctx.edit_headers.x_edit_summary,
        )
        event_context = EventPublishContext(
            entity_id=ctx.entity_id,
            revision_id=1,
            change_type=ChangeType.CREATION,
            from_revision_id=0,
            changed_at=datetime.now(),
        )
        ctx.tx.publish_event(event_context, edit_context)
        logger.debug("🔍 HANDLER: Event published successfully")

        ctx.tx.commit()
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
            tx_ctx = CreationTransactionContext(
                tx=tx,
                entity_id=entity_id,
                request_data=request_data,
                request=request,
                edit_headers=edit_headers,
                validator=validator,
            )
            response = await self._execute_creation_transaction(tx_ctx)

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
