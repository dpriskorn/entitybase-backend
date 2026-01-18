"""Entity redirect service."""

import logging
from datetime import timezone
from typing import TYPE_CHECKING

from models.infrastructure.stream.producer import StreamProducerClient
from models.rest_api.entitybase.request.entity import EntityRedirectRequest
from models.rest_api.entitybase.response import (
    EntityRedirectResponse,
)
from models.rest_api.entitybase.response.entity import EntityRevertResponse
from models.infrastructure.s3.enums import EditType
from models.rest_api.utils import raise_validation_error

if TYPE_CHECKING:
    from models.infrastructure.s3.s3_client import MyS3Client
    from models.infrastructure.vitess_client import VitessClient
    from models.infrastructure.stream.producer import StreamProducerClient
    from models.infrastructure.stream.event import EntityChangeEvent
    from models.infrastructure.stream.change_type import ChangeType

logger = logging.getLogger(__name__)


class RedirectService:
    """Service for managing entity redirects"""

    def __init__(
        self,
        s3_client: "MyS3Client",
        vitess_client: "VitessClient",
        stream_producer: StreamProducerClient | None = None,
    ):
        self.s3 = s3_client
        self.vitess = vitess_client
        self.stream_producer = stream_producer

    async def create_redirect(
        self,
        request: EntityRedirectRequest,
    ) -> EntityRedirectResponse:
        """Mark an entity as redirect to another entity"""
        logger.debug(
            "Creating redirect from %s to %s",
            request.redirect_from_id,
            request.redirect_to_id,
        )
        from datetime import datetime

        if request.redirect_from_id == request.redirect_to_id:
            raise_validation_error("Cannot redirect to self", status_code=400)

        existing_target = self.vitess.get_redirect_target(request.redirect_from_id)
        if existing_target:
            raise_validation_error("Redirect already exists", status_code=409)

        if self.vitess.is_entity_deleted(request.redirect_from_id):
            raise_validation_error("Source entity has been deleted", status_code=423)
        if self.vitess.is_entity_deleted(request.redirect_to_id):
            raise_validation_error("Target entity has been deleted", status_code=423)

        if self.vitess.is_entity_locked(
            request.redirect_to_id
        ) or self.vitess.is_entity_archived(request.redirect_to_id):
            raise_validation_error(
                "Target entity is locked or archived", status_code=423
            )

        to_head_revision_id = self.vitess.get_head(request.redirect_to_id)
        if to_head_revision_id == 0:
            raise_validation_error("Target entity has no revisions", status_code=404)

        from_head_revision_id = self.vitess.get_head(request.redirect_from_id)
        redirect_revision_id = from_head_revision_id + 1 if from_head_revision_id else 1

        redirect_revision_data = {
            "schema_version": "1.1.0",
            "redirects_to": request.redirect_to_id,
            "entity": {
                "id": request.redirect_from_id,
                "type": "item",
                "labels": {},
                "descriptions": {},
                "aliases": {},
                "claims": {},
                "sitelinks": {},
            },
        }

        self.s3.write_revision(
            entity_id=request.redirect_from_id,
            revision_id=redirect_revision_id,
            data=redirect_revision_data,
            publication_state="pending",
        )

        self.vitess.insert_revision(
            request.redirect_from_id,
            redirect_revision_id,
            is_mass_edit=False,
            edit_type=EditType.REDIRECT_CREATE.value,
            statements=[],
            properties=[],
            property_counts={},
        )

        self.vitess.create_redirect(
            redirect_from_entity_id=request.redirect_from_id,
            redirect_to_entity_id=request.redirect_to_id,
            created_by=request.created_by,
        )

        self.vitess.set_redirect_target(
            entity_id=request.redirect_from_id,
            redirects_to_entity_id=request.redirect_to_id,
        )

        self.s3.mark_published(
            entity_id=request.redirect_from_id,
            revision_id=redirect_revision_id,
            publication_state="published",
        )

        if self.stream_producer:
            event = EntityChangeEvent(
                id=request.redirect_from_id,
                rev=redirect_revision_id,
                type=ChangeType.REDIRECT,
                from_rev=from_head_revision_id if from_head_revision_id else None,
                at=datetime.now(timezone.utc),
                summary=request.revert_reason,
            )
            await self.stream_producer.publish_change(event)

        return EntityRedirectResponse(
            redirect_from_id=request.redirect_from_id,
            redirect_to_id=request.redirect_to_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            revision_id=redirect_revision_id,
        )

    async def revert_redirect(
        self,
        entity_id: str,
        revert_to_revision_id: int,
        user_id: int,
    ) -> EntityRevertResponse:
        """Revert a redirect entity back to normal using the general revert."""
        logger.debug(
            "Reverting redirect for entity %s to revision %d",
            entity_id,
            revert_to_revision_id,
        )
        current_redirect_target = self.vitess.get_redirect_target(entity_id)

        if not current_redirect_target:
            raise_validation_error("Entity is not a redirect", status_code=404)

        if self.vitess.is_entity_deleted(entity_id):
            raise_validation_error("Entity has been deleted", status_code=423)

        if self.vitess.is_entity_locked(entity_id) or self.vitess.is_entity_archived(
            entity_id
        ):
            raise_validation_error("Entity is locked or archived", status_code=423)

        # Call general revert
        from models.rest_api.entitybase.handlers.entity.revert import (
            EntityRevertHandler,
        )
        from models.rest_api.entitybase.request.entity import EntityRevertRequest

        general_request = EntityRevertRequest(
            to_revision_id=revert_to_revision_id,
            reason="Reverted redirect",
            watchlist_context=None,
        )
        general_handler = EntityRevertHandler()
        revert_result = await general_handler.revert_entity(
            entity_id,
            general_request,
            self.vitess,
            self.s3,
            self.stream_producer,
            user_id,
        )

        # Clear the redirect target
        self.vitess.revert_redirect(entity_id)

        return revert_result
