"""Entity redirect service."""

import logging
from datetime import timezone, datetime
from typing import TYPE_CHECKING

from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from models.data.infrastructure.s3.entity_state import EntityState
from models.data.infrastructure.s3.enums import EditData, EntityType, EditType
from models.data.infrastructure.s3.hashes.hash_maps import HashMaps
from models.infrastructure.s3.revision.revision_data import RevisionData
from models.data.rest_api.v1.entitybase.request import EntityRedirectRequest
from models.data.rest_api.v1.entitybase.response import (
    EntityRedirectResponse,
)
from models.data.rest_api.v1.entitybase.response import EntityRevertResponse
from models.rest_api.entitybase.v1.service import Service
from models.rest_api.utils import raise_validation_error

if TYPE_CHECKING:
    from models.infrastructure.stream.event import EntityChangeEvent
    from models.data.infrastructure.stream.change_type import ChangeType

logger = logging.getLogger(__name__)


class RedirectService(Service):
    """Service for managing entity redirects"""

    async def create_redirect(
        self,
        request: EntityRedirectRequest,
        edit_headers: EditHeaders,
    ) -> EntityRedirectResponse:
        """Mark an entity as redirect to another entity"""
        logger.debug(
            "Creating redirect from %s to %s",
            request.redirect_from_id,
            request.redirect_to_id,
        )

        if request.redirect_from_id == request.redirect_to_id:
            raise_validation_error("Cannot redirect to self", status_code=400)

        existing_target = self.vitess_client.get_redirect_target(
            request.redirect_from_id
        )
        if existing_target:
            raise_validation_error("Redirect already exists", status_code=409)

        if self.vitess_client.is_entity_deleted(request.redirect_from_id):
            raise_validation_error("Source entity has been deleted", status_code=423)
        if self.vitess_client.is_entity_deleted(request.redirect_to_id):
            raise_validation_error("Target entity has been deleted", status_code=423)

        if self.vitess_client.is_entity_locked(
            request.redirect_to_id
        ) or self.vitess_client.is_entity_archived(request.redirect_to_id):
            raise_validation_error(
                "Target entity is locked or archived", status_code=423
            )

        to_head_revision_id = self.vitess_client.get_head(request.redirect_to_id)
        if to_head_revision_id == 0:
            raise_validation_error("Target entity has no revisions", status_code=404)

        from_head_revision_id = self.vitess_client.get_head(request.redirect_from_id)
        redirect_revision_id = from_head_revision_id + 1 if from_head_revision_id else 1

        redirect_revision_data = RevisionData(
            revision_id=redirect_revision_id,
            entity_type=EntityType.ITEM,
            edit=EditData(
                type=EditType.REDIRECT_CREATE,
                at=datetime.now(timezone.utc).isoformat(),
                summary=edit_headers.x_edit_summary,
                user_id=edit_headers.x_user_id,
            ),
            hashes=HashMaps(),
            redirects_to=request.redirect_to_id,
            state=EntityState(),
        )

        import json
        from models.internal_representation.metadata_extractor import MetadataExtractor
        from models.data.infrastructure.s3.revision_data import S3RevisionData
        from models.config.settings import settings

        revision_dict = redirect_revision_data.model_dump(mode="json")
        revision_json = json.dumps(revision_dict, sort_keys=True)
        content_hash = MetadataExtractor.hash_string(revision_json)

        s3_revision_data = S3RevisionData(
            schema=settings.s3_schema_revision_version,
            revision=revision_dict,
            hash=content_hash,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        self.state.s3_client.store_revision(content_hash, s3_revision_data)

        self.vitess_client.create_revision(
            entity_id=request.redirect_from_id,
            revision_id=redirect_revision_id,
            entity_data=redirect_revision_data,
            expected_revision_id=from_head_revision_id,
            content_hash=content_hash,
        )

        self.vitess_client.create_redirect(
            redirect_from_entity_id=request.redirect_from_id,
            redirect_to_entity_id=request.redirect_to_id,
            created_by=request.created_by,
        )

        self.vitess_client.set_redirect_target(
            entity_id=request.redirect_from_id,
            redirects_to_entity_id=request.redirect_to_id,
        )

        self.state.s3_client.mark_published(
            entity_id=request.redirect_from_id,
            revision_id=redirect_revision_id,
            publication_state="published",
        )

        if self.state.entity_change_stream_producer:
            event = EntityChangeEvent(
                id=request.redirect_from_id,
                rev=redirect_revision_id,
                type=ChangeType.REDIRECT,
                from_rev=from_head_revision_id if from_head_revision_id else None,
                at=datetime.now(timezone.utc),
                summary=edit_headers.x_edit_summary,
            )
            await self.state.entity_change_stream_producer.publish_event(event)

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
        edit_headers: EditHeaders,
    ) -> EntityRevertResponse:
        """Revert a redirect entity back to normal using the general revert."""
        logger.debug(
            "Reverting redirect for entity %s to revision %d",
            entity_id,
            revert_to_revision_id,
        )
        current_redirect_target = self.vitess_client.get_redirect_target(entity_id)

        if not current_redirect_target:
            raise_validation_error("Entity is not a redirect", status_code=404)

        if self.vitess_client.is_entity_deleted(entity_id):
            raise_validation_error("Entity has been deleted", status_code=423)

        if self.vitess_client.is_entity_locked(
            entity_id
        ) or self.vitess_client.is_entity_archived(entity_id):
            raise_validation_error("Entity is locked or archived", status_code=423)

        # Call general revert
        from models.rest_api.entitybase.v1.handlers.entity.revert import (
            EntityRevertHandler,
        )
        from models.data.rest_api.v1.entitybase.request import EntityRevertRequest

        general_request = EntityRevertRequest(
            to_revision_id=revert_to_revision_id,
            watchlist_context=None,
        )
        general_handler = EntityRevertHandler(state=self.state)
        revert_result = await general_handler.revert_entity(
            entity_id, general_request, edit_headers=edit_headers
        )

        # Clear the redirect target
        self.vitess_client.revert_redirect(entity_id)

        return revert_result
