"""Entity creation transaction management."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from models.data.infrastructure.stream.change_type import ChangeType
from models.data.rest_api.v1.entitybase.request.entity import PreparedRequestData
from models.data.rest_api.v1.entitybase.request.edit_context import EditContext
from models.data.rest_api.v1.entitybase.request.entity.context import EventPublishContext
from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from models.data.rest_api.v1.entitybase.response import EntityResponse
from models.data.rest_api.v1.entitybase.response import StatementHashResult
from models.rest_api.entitybase.v1.handlers.entity.entity_transaction import (
    EntityTransaction,
)

logger = logging.getLogger(__name__)


class CreationTransaction(EntityTransaction):
    def process_statements(
        self,
        entity_id: str,
        request_data: PreparedRequestData,
        validator: Any,
    ) -> StatementHashResult:
        """Process statements for the entity transaction."""
        logger.info(
            f"[CreationTransaction] Starting statement processing for {entity_id}"
        )
        # Import here to avoid circular imports
        from models.rest_api.entitybase.v1.handlers.entity.handler import EntityHandler

        handler = EntityHandler(state=self.state)
        hash_result = handler.process_statements(entity_id, request_data, validator)
        # Track hashes for rollback
        self.statement_hashes.extend(hash_result.statements)
        for hash_val in hash_result.statements:
            self.operations.append(
                lambda h=hash_val: self._rollback_statement(h)  # type: ignore[misc]
            )
        return hash_result

    async def create_revision(
        self,
        entity_id: str,
        request_data: PreparedRequestData,
        entity_type: Any,
        edit_headers: EditHeaders,
        hash_result: StatementHashResult,
    ) -> EntityResponse:
        """Create revision using new architecture components."""
        logger.debug(f"Creating revision for {entity_id}")
        
        from models.rest_api.entitybase.v1.services.hash_service import HashService
        from models.data.infrastructure.s3.enums import EditType, EditData
        from models.data.infrastructure.s3.entity_state import EntityState
        import json
        from rapidhash import rapidhash
        from models.internal_representation.metadata_extractor import MetadataExtractor
        from models.data.infrastructure.s3.revision_data import S3RevisionData
        from models.data.infrastructure.s3.hashes.hash_maps import HashMaps
        from models.data.infrastructure.s3.hashes.statements_hashes import StatementsHashes
        from models.infrastructure.s3.revision.revision_data import RevisionData
        from models.config.settings import settings
        
        entity_json = json.dumps(request_data.model_dump(mode="json"), sort_keys=True)
        content_hash = rapidhash(entity_json.encode())
        
        hs = HashService(state=self.state)
        sitelink_hashes = hs.hash_sitelinks(request_data.sitelinks)
        labels_hashes = hs.hash_labels(request_data.labels)
        descriptions_hashes = hs.hash_descriptions(request_data.descriptions)
        aliases_hashes = hs.hash_aliases(request_data.aliases)
        
        created_at = datetime.now().isoformat()

        # noinspection PyArgumentList
        revision_data = RevisionData(
            revision_id=1,
            entity_type=entity_type,
            properties=hash_result.properties,
            property_counts=hash_result.property_counts,
            hashes=HashMaps(
                statements=StatementsHashes(root=hash_result.statements),
                sitelinks=sitelink_hashes,
                labels=labels_hashes,
                descriptions=descriptions_hashes,
                aliases=aliases_hashes,
            ),
            edit=EditData(
                mass=False,
                type=EditType.UNSPECIFIED,
                user_id=edit_headers.x_user_id,
                summary=edit_headers.x_edit_summary,
                at=created_at,
            ),
            state=EntityState(),
            schema_version=settings.s3_schema_revision_version,
        )
        
        self.state.vitess_client.create_revision(
            entity_id=entity_id,
            entity_data=revision_data,
            revision_id=1,
            content_hash=content_hash,
        )
        
        revision_dict = revision_data.model_dump(mode="json")
        revision_json = json.dumps(revision_dict, sort_keys=True)
        content_hash = MetadataExtractor.hash_string(revision_json)
        
        s3_revision_data = S3RevisionData(
            schema=settings.s3_schema_revision_version,
            revision=revision_dict,
            hash=content_hash,
            created_at=created_at,
        )
        
        self.state.s3_client.store_revision(content_hash, s3_revision_data)
        
        self.operations.append(
            lambda: self._rollback_revision(entity_id, 1)
        )
        
        return EntityResponse(
            id=entity_id,
            rev_id=1,
            data=s3_revision_data,
            state=EntityState(),
        )

    def publish_event(
        self,
        event_context: EventPublishContext,
        edit_context: EditContext,
    ) -> None:
        """Publish the entity creation event."""
        changed_at = event_context.changed_at
        if changed_at is None:
            changed_at = datetime.now()
        logger.info(f"[CreationTransaction] Starting event publishing for {event_context.entity_id}")
        if self.state.entity_change_stream_producer:
            from models.infrastructure.stream.event import EntityChangeEvent

            event = EntityChangeEvent(
                id=event_context.entity_id,
                rev=event_context.revision_id,
                type=ChangeType(event_context.change_type),
                from_rev=event_context.from_revision_id,
                at=changed_at,
                summary=edit_context.edit_summary,
            )
            self.state.entity_change_stream_producer.publish_change(event)
        # Events are fire-and-forget, no rollback needed

    def commit(self) -> None:
        """Commit the creation transaction."""
        logger.info(f"[CreationTransaction] Committing creation for {self.entity_id}")

        self.operations.clear()  # Prevent rollback after commit

    def rollback(self) -> None:
        """Rollback the creation transaction."""
        logger.info(f"[CreationTransaction] Rolling back creation for {self.entity_id}")
        for op in reversed(self.operations):
            try:
                op()
            except Exception as e:
                logger.warning(f"[CreationTransaction] Rollback operation failed: {e}")
        self.operations.clear()

    # Private rollback methods
    def _rollback_entity_registration(self) -> None:
        logger.info(
            f"[CreationTransaction] Rolling back entity registration for {self.entity_id}"
        )
        # TODO: Delete from entity_id_mapping if possible
        # Since register_entity just inserts, and we assume no conflicts, perhaps no action needed
        pass

    def _rollback_statement(self, hash_val: int) -> None:
        logger.info(f"[CreationTransaction] Rolling back statement {hash_val}")
        # Decrement ref_count
        self.state.vitess_client.decrement_ref_count(hash_val)
        # Check if orphaned and delete from S3
        ref_count = self.state.vitess_client.get_ref_count(hash_val)
        if ref_count == 0:
            self.state.s3_client.delete_statement(hash_val)

    def _rollback_revision(self, entity_id: str, revision_id: int) -> None:
        logger.info(
            f"[CreationTransaction] Rolling back revision {revision_id} for {entity_id}"
        )
        # Delete from entity_revisions and entity_head
        self.state.vitess_client.delete_revision(entity_id, revision_id)
        # S3 deletion if needed, but assume Vitess handles it or add s3_client.delete_revision
