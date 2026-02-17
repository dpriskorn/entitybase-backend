"""Handler for entity revert operations."""

import logging
from datetime import datetime, timezone
from typing import cast

from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from models.data.infrastructure.s3.entity_state import EntityState
from models.data.infrastructure.s3.enums import EditType, EditData
from models.data.infrastructure.s3.hashes.hash_maps import HashMaps

from models.data.infrastructure.stream.change_type import ChangeType
from models.infrastructure.s3.revision.revision_data import RevisionData
from models.infrastructure.stream.event import EntityChangeEvent
from models.rest_api.entitybase.v1.handler import Handler
from models.data.rest_api.v1.entitybase.request import EntityRevertRequest
from models.data.rest_api.v1.entitybase.response import EntityRevertResponse
from models.rest_api.utils import raise_validation_error

logger = logging.getLogger(__name__)


class EntityRevertHandler(Handler):
    """Handler for reverting entities to previous revisions."""

    async def revert_entity(
        self,
        entity_id: str,
        request: EntityRevertRequest,
        edit_headers: EditHeaders,
    ) -> EntityRevertResponse:
        """Revert an entity to a specified revision."""
        logger.debug(
            f"Reverting entity {entity_id} to revision {request.to_revision_id}"
        )

        internal_entity_id = await self._resolve_entity_id(entity_id)
        target_revision = await self._get_target_revision(
            entity_id, request.to_revision_id, internal_entity_id
        )
        target_revision_data = await self._read_target_revision_from_s3(
            entity_id, request.to_revision_id
        )
        head_revision = await self._get_head_revision(internal_entity_id)

        self._validate_revert_target(entity_id, request.to_revision_id, head_revision)

        new_revision_id = head_revision + 1
        logger.debug(f"New revision ID: {new_revision_id}")

        new_revision_data = await self._create_revision_data(
            entity_id, target_revision_data, new_revision_id, edit_headers
        )

        content_hash = await self._store_revision(
            entity_id, new_revision_id, new_revision_data
        )

        await self._publish_change_event(
            entity_id, new_revision_id, head_revision, edit_headers
        )

        return EntityRevertResponse(
            entity_id=entity_id,
            new_rev_id=new_revision_id,
            from_rev_id=head_revision,
            reverted_at=datetime.now(timezone.utc).isoformat(),
        )

    async def _resolve_entity_id(self, entity_id: str) -> int:
        """Resolve internal entity ID from entity ID."""
        logger.debug("Resolving internal entity ID")
        internal_entity_id = cast(int, self.state.vitess_client.id_resolver.resolve_id(entity_id))
        if internal_entity_id == 0:
            raise_validation_error(f"Entity {entity_id} not found", status_code=404)
        return internal_entity_id

    async def _get_target_revision(
        self, entity_id: str, to_revision_id: int, internal_entity_id: int
    ) -> RevisionData:
        """Get target revision from database."""
        target_revision = cast(RevisionData, self.state.vitess_client.revision_repository.get_revision(
            internal_entity_id, to_revision_id
        ))
        if not target_revision:
            raise_validation_error(
                f"Revision {to_revision_id} not found for entity {entity_id}",
                status_code=404,
            )
        return target_revision

    async def _read_target_revision_from_s3(
        self, entity_id: str, to_revision_id: int
    ) -> dict:
        """Read target revision content from S3."""
        target_revision_data = cast(dict, self.state.s3_client.read_full_revision(
            entity_id, to_revision_id
        ))
        return (
            target_revision_data.revision
            if hasattr(target_revision_data, "revision")
            else target_revision_data
        )

    async def _get_head_revision(self, internal_entity_id: int) -> int:
        """Get current head revision."""
        head_result = self.state.vitess_client.head_repository.get_head_revision(
            internal_entity_id
        )
        if not head_result.success:
            raise_validation_error(
                head_result.error or "Failed to get head revision", status_code=500
            )
        head_revision = head_result.data if isinstance(head_result.data, int) else 0
        return head_revision

    def _validate_revert_target(
        self, entity_id: str, to_revision_id: int, head_revision: int
    ) -> None:
        """Validate that revert target is different from current head."""
        if head_revision == to_revision_id:
            raise_validation_error(
                f"Entity {entity_id} is already at revision {to_revision_id}",
                status_code=400,
            )

    async def _create_revision_data(
        self,
        entity_id: str,
        target_data: dict,
        new_revision_id: int,
        edit_headers: EditHeaders,
    ) -> RevisionData:
        """Create new revision data from target revision."""
        logger.debug("Creating new revision data from target revision")

        target_hashes = target_data.get("hashes", {})
        if isinstance(target_hashes, dict):
            hashes = HashMaps(
                statements=target_hashes.get("statements"),
                labels=target_hashes.get("labels"),
                descriptions=target_hashes.get("descriptions"),
                aliases=target_hashes.get("aliases"),
                sitelinks=target_hashes.get("sitelinks"),
            )
        else:
            hashes = HashMaps()

        target_state = target_data.get("state", {})
        if isinstance(target_state, dict):
            state = EntityState(
                sp=target_state.get("sp", target_state.get("is_semi_protected", False)),
                locked=target_state.get("locked", target_state.get("is_locked", False)),
                archived=target_state.get(
                    "archived", target_state.get("is_archived", False)
                ),
                dangling=target_state.get(
                    "dangling", target_state.get("is_dangling", False)
                ),
                mep=target_state.get(
                    "mep", target_state.get("is_mass_edit_protected", False)
                ),
                deleted=target_state.get(
                    "deleted", target_state.get("is_deleted", False)
                ),
            )
        else:
            state = EntityState()

        return RevisionData(
            revision_id=new_revision_id,
            entity_type=target_data.get("entity_type", "item"),
            edit=EditData(
                type=EditType.MANUAL_UPDATE,
                user_id=edit_headers.x_user_id,
                summary=f"Revert to revision {new_revision_id - 1}",
                at=datetime.now(timezone.utc).isoformat(),
            ),
            hashes=hashes,
            redirects_to="",
            state=state,
            property_counts=target_data.get("property_counts"),
            properties=target_data.get("properties", []),
        )

    async def _store_revision(
        self, entity_id: str, new_revision_id: int, new_revision_data: RevisionData
    ) -> str:
        """Store revision to S3 and database."""
        logger.debug("Converting revision to dict and computing hash")
        import json
        from models.internal_representation.metadata_extractor import MetadataExtractor
        from models.data.infrastructure.s3.revision_data import S3RevisionData
        from models.config.settings import settings

        revision_dict = new_revision_data.model_dump(mode="json")
        revision_json = json.dumps(revision_dict, sort_keys=True)
        content_hash = MetadataExtractor.hash_string(revision_json)
        logger.debug(f"Content hash: {content_hash}")

        s3_revision_data = S3RevisionData(
            schema=settings.s3_schema_revision_version,
            revision=revision_dict,
            hash=content_hash,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        logger.debug("Storing revision to S3")
        self.state.s3_client.store_revision(content_hash, s3_revision_data)

        logger.debug("Inserting revision in Vitess")
        self.state.vitess_client.insert_revision(
            entity_id,
            new_revision_id,
            new_revision_data,
            content_hash,
        )

        return content_hash

    async def _publish_change_event(
        self,
        entity_id: str,
        new_revision_id: int,
        head_revision: int,
        edit_headers: EditHeaders,
    ) -> None:
        """Publish entity change event."""
        if self.state.entity_change_stream_producer:
            event = EntityChangeEvent(
                id=entity_id,
                rev=new_revision_id,
                type=ChangeType.REVERT,
                from_rev=head_revision,
                at=datetime.now(timezone.utc),
                summary=edit_headers.x_edit_summary,
            )
            await self.state.entity_change_stream_producer.publish_event(event)
