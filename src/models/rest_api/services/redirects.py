from datetime import datetime, timezone

from models.rest_api.misc import EditType
from models.rest_api.request.entity import EntityRedirectRequest
from models.rest_api.response.entity import EntityRedirectResponse, EntityResponse
from models.validation.utils import raise_validation_error
from models.infrastructure.s3.s3_client import S3Client
from models.infrastructure.stream import (
    ChangeType,
    EntityChangeEvent,
    StreamProducerClient,
)
from models.infrastructure.vitess_client import VitessClient


class RedirectService:
    """Service for managing entity redirects"""

    def __init__(
        self,
        s3_client: S3Client,
        vitess_client: VitessClient,
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
        from datetime import datetime

        if request.redirect_from_id == request.redirect_to_id:
            raise_validation_error("Cannot redirect to self", status_code=400)

        existing_target = self.vitess.get_redirect_target(request.redirect_from_id)
        if existing_target is not None:
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
                entity_id=request.redirect_from_id,
                revision_id=redirect_revision_id,
                change_type=ChangeType.REDIRECT,
                from_revision_id=from_head_revision_id
                if from_head_revision_id
                else None,
                changed_at=datetime.now(timezone.utc),
                editor=request.created_by,
                edit_summary=None,
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
    ) -> EntityResponse:
        """Revert a redirect entity back to normal using revision-based restore"""
        current_redirect_target = self.vitess.get_redirect_target(entity_id)

        if current_redirect_target is None:
            raise_validation_error("Entity is not a redirect", status_code=404)

        if self.vitess.is_entity_deleted(entity_id):
            raise_validation_error("Entity has been deleted", status_code=423)

        if self.vitess.is_entity_locked(entity_id) or self.vitess.is_entity_archived(
            entity_id
        ):
            raise_validation_error("Entity is locked or archived", status_code=423)

        head_revision_id = self.vitess.get_head(entity_id)
        new_revision_id = head_revision_id + 1 if head_revision_id else 1

        target_revision = self.s3.read_full_revision(entity_id, revert_to_revision_id)
        target_data = target_revision

        new_revision_data = {
            "schema_version": "1.1.0",
            "redirects_to": None,
            "entity": target_data["entity"],
        }

        self.s3.write_revision(
            entity_id=entity_id,
            revision_id=new_revision_id,
            data=new_revision_data,
            publication_state="pending",
        )

        self.vitess.insert_revision(
            entity_id,
            new_revision_id,
            is_mass_edit=False,
            edit_type=EditType.REDIRECT_REVERT.value,
            statements=[],
            properties=[],
            property_counts={},
        )

        self.vitess.set_redirect_target(
            entity_id=entity_id,
            redirects_to_entity_id=None,
        )

        self.s3.mark_published(
            entity_id=entity_id,
            revision_id=new_revision_id,
            publication_state="published",
        )

        if self.stream_producer:
            event = EntityChangeEvent(
                entity_id=entity_id,
                revision_id=new_revision_id,
                change_type=ChangeType.UNREDIRECT,
                from_revision_id=head_revision_id,
                changed_at=datetime.now(timezone.utc),
                editor=None,
                edit_summary=None,
            )
            await self.stream_producer.publish_change(event)

        return EntityResponse(
            id=entity_id, revision_id=new_revision_id, data=new_revision_data["entity"]
        )
