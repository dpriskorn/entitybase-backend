import logging
from typing import Any

from models.api_models import EntityCreateRequest, EntityResponse
from models.infrastructure.s3.s3_client import S3Client
from models.infrastructure.stream.producer import StreamProducerClient
from models.infrastructure.vitess_client import VitessClient
from models.validation.utils import raise_validation_error
from models.rest_api.services.enumeration_service import EnumerationService
from .create import EntityCreateHandler
from .creation_transaction import CreationTransaction

logger = logging.getLogger(__name__)


class ItemCreateHandler(EntityCreateHandler):
    """Handler for item creation operations"""

    def __init__(self, enumeration_service: EnumerationService, /, **data: Any):
        super().__init__(**data)
        self.enumeration_service = enumeration_service

    async def create_entity(
        self,
        request: EntityCreateRequest,
        vitess_client: VitessClient,
        s3_client: S3Client,
        stream_producer: StreamProducerClient | None,
        validator: Any | None = None,
        auto_assign_id: bool = False,
    ) -> EntityResponse:
        """Create a new item with auto-assigned Q ID using CreationTransaction."""
        # Auto-assign ID
        if self.enumeration_service is None:
            raise_validation_error("Enumeration service not available", status_code=500)
        assert self.enumeration_service is not None
        entity_id = self.enumeration_service.get_next_entity_id("item")
        request.id = entity_id

        # Prepare request data
        request_data = request.data.copy()
        request_data["id"] = entity_id

        # Create transaction
        tx = CreationTransaction()
        try:
            # Register entity
            tx.register_entity(vitess_client, entity_id)

            # Process statements
            hash_result = tx.process_statements(
                entity_id, request_data, vitess_client, s3_client, validator
            )

            # Create revision
            response = await tx.create_revision(
                entity_id=entity_id,
                new_revision_id=1,
                head_revision_id=0,
                request_data=request_data,
                entity_type="item",
                hash_result=hash_result,
                content_hash=0,
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

            # Publish event
            tx.publish_event(
                entity_id=entity_id,
                revision_id=1,
                change_type="creation",
                from_revision_id=None,
                changed_at=None,
                editor=request.editor,
                edit_summary=request.edit_summary,
                stream_producer=stream_producer,
            )

            # Commit
            tx.commit()

            # Confirm ID usage to worker
            self.enumeration_service.confirm_id_usage(entity_id)

            return response
        except Exception as e:
            logger.error(f"Item creation failed for {entity_id}: {e}")
            tx.rollback()
            raise
