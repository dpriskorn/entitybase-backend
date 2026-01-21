"""Item-specific entity handlers."""

import logging
import traceback
from datetime import datetime
from typing import Any

from models.infrastructure.s3.enums import EntityType
from models.infrastructure.stream.change_type import ChangeType
from models.rest_api.entitybase.v1.request import EntityCreateRequest
from models.rest_api.entitybase.v1.response import EntityResponse
from models.rest_api.utils import raise_validation_error
from .create import EntityCreateHandler
from .creation_transaction import CreationTransaction

logger = logging.getLogger(__name__)


class ItemCreateHandler(EntityCreateHandler):
    """Handler for item creation operations"""

    async def create_entity(
        self,
        request: EntityCreateRequest,
        validator: Any | None = None,
        auto_assign_id: bool = False,
        user_id: int = 0,
    ) -> EntityResponse:
        """Create a new item with auto-assigned Q ID using EntityTransaction."""
        logger.info(f"🔍 HANDLER: Starting item creation for {request.id or 'auto-assign'}")
        logger.debug(f"🔍 HANDLER: Request: {request.model_dump()}")
        entity_id = request.id
        # Check database connectivity
        if entity_id:
            # Check if entity already exists
            try:
                exists = self.state.vitess_client.id_resolver.entity_exists(entity_id)
                logger.debug(f"🔍 HANDLER: Entity exists check: {exists}")
                if exists:
                    logger.error(f"🔍 HANDLER: Entity {entity_id} already exists")
                    raise_validation_error("Entity already exists", status_code=409)
            except Exception as e:
                logger.error(f"🔍 HANDLER: Database connection error during existence check: {e}")
                raise
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

        # Prepare request data
        logger.info("🔍 HANDLER: Preparing request data")
        request_data = request.data.copy()
        request_data["id"] = entity_id
        logger.debug(f"🔍 HANDLER: Prepared request data: {request_data}")

        # Create transaction
        logger.info("🔍 HANDLER: Creating transaction")
        tx = CreationTransaction(state=self.state)
        logger.debug("🔍 HANDLER: Transaction created successfully")
        try:
            # Register entity
            logger.info(f"🔍 HANDLER: Registering entity {entity_id}")
            tx.register_entity(entity_id)  # type: ignore[attr-defined]
            logger.debug(f"🔍 HANDLER: Entity {entity_id} registered successfully")

            # Process statements
            logger.info("🔍 HANDLER: Processing statements")
            hash_result = tx.process_statements(entity_id, request_data, validator)
            logger.debug(f"🔍 HANDLER: Statements processed, hash_result: {hash_result}")

            # Create revision
            logger.info("🔍 HANDLER: Creating revision")
            response = await tx.create_revision(
                entity_id=entity_id,
                new_revision_id=1,
                head_revision_id=0,
                request_data=request_data,
                entity_type=EntityType.ITEM,
                hash_result=hash_result,
                is_mass_edit=request.is_mass_edit,
                edit_type=request.edit_type,
                edit_summary=request.edit_summary,
                is_semi_protected=request.state.is_semi_protected,
                is_locked=request.state.is_locked,
                is_archived=request.state.is_archived,
                is_dangling=request.state.is_dangling,
                is_mass_edit_protected=request.state.is_mass_edit_protected,
                is_creation=True,
                user_id=request.user_id,
            )
            logger.debug(f"🔍 HANDLER: Revision created: {response}")

            # Publish event
            logger.info("🔍 HANDLER: Publishing event")
            tx.publish_event(
                entity_id=entity_id,
                revision_id=1,
                change_type=ChangeType.CREATION,
                changed_at=datetime.now(),
                # stream_producer=stream_producer,
                # from_revision_id=0,
                # edit_summary=request.edit_summary,
            )
            logger.debug("🔍 HANDLER: Event published successfully")

            # Commit
            logger.info("🔍 HANDLER: Committing transaction")
            tx.commit()
            logger.debug("🔍 HANDLER: Transaction committed successfully")

            # Confirm ID usage to worker
            if self.enumeration_service:
                assert self.enumeration_service is not None
                self.enumeration_service.confirm_id_usage(entity_id)

            logger.info(f"Item creation successful for {entity_id}")
            return response  # type: ignore[no-any-return]
        except Exception as e:
            logger.error(
                f"Item creation failed for {entity_id}: {e}\n{traceback.format_exc()}"
            )
            tx.rollback()
            raise
