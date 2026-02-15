"""Entity update transaction management."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Callable

from models.data.infrastructure.s3 import EntityState
from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from models.data.infrastructure.s3.enums import MetadataType
from models.data.infrastructure.stream.change_type import ChangeType
from models.data.rest_api.v1.entitybase.request.entity import PreparedRequestData
from models.data.rest_api.v1.entitybase.request.edit_context import EditContext
from models.data.rest_api.v1.entitybase.request.entity.context import (
    EventPublishContext,
)
from models.data.rest_api.v1.entitybase.response import EntityResponse
from models.data.rest_api.v1.entitybase.response import StatementHashResult
from models.rest_api.entitybase.v1.endpoints.lexeme_utils import (
    assign_form_ids,
    assign_sense_ids,
)
from models.rest_api.entitybase.v1.handlers.entity.entity_transaction import (
    EntityTransaction,
)
from models.rest_api.entitybase.v1.services.statement_service import StatementService

logger = logging.getLogger(__name__)


class UpdateTransaction(EntityTransaction):
    """Transaction for updating entities."""

    lexeme_term_operations: list[Callable[[], None]] = []

    def process_lexeme_terms(
        self,
        forms: list[dict[str, Any]],
        senses: list[dict[str, Any]],
        lemmas: dict[str, dict[str, Any]] | None = None,
    ) -> None:
        """Process lexeme terms (lemmas, forms and senses) for S3 storage.

        Args:
            forms: List of form data with representations
            senses: List of sense data with glosses
            lemmas: Lexeme lemmas dict keyed by language
        """
        logger.info("[UpdateTransaction] Starting lexeme term processing")

        from models.rest_api.entitybase.v1.utils.lexeme_term_processor import (
            LexemeTermProcessorConfig,
            process_lexeme_terms,
        )

        config = LexemeTermProcessorConfig(
            s3_client=self.state.s3_client,
            lemmas=lemmas,
            on_form_stored=lambda h: self.lexeme_term_operations.append(
                lambda: self._rollback_form_representation(h)
            ),
            on_gloss_stored=lambda h: self.lexeme_term_operations.append(
                lambda: self._rollback_sense_gloss(h)
            ),
            on_lemma_stored=lambda h: self.lexeme_term_operations.append(
                lambda: self._rollback_lemma(h)
            ),
        )

        process_lexeme_terms(
            forms=forms,
            senses=senses,
            config=config,
        )

        logger.info("[UpdateTransaction] Completed lexeme term processing")

    def process_statements(
        self,
        entity_id: str,
        request_data: PreparedRequestData,
        validator: Any,
    ) -> StatementHashResult:
        """Process statements for the entity transaction."""
        logger.info(
            f"[UpdateTransaction] Starting statement processing for {entity_id}"
        )
        # Import here to avoid circular imports
        ss = StatementService(state=self.state)

        hash_result = ss.hash_entity_statements(request_data)
        if not hash_result.success:
            from models.rest_api.utils import raise_validation_error

            raise_validation_error(
                f"Failed to hash statements: {hash_result.error}", status_code=500
            )

        # Store new statements
        hash_data = hash_result.get_data()
        store_result = ss.deduplicate_and_store_statements(hash_data, validator)
        if not store_result.success:
            from models.rest_api.utils import raise_validation_error

            raise_validation_error(
                f"Failed to store statements: {store_result.error}", status_code=500
            )

        # Record hashes for rollback
        self.statement_hashes.extend(hash_data.statements)
        for hash_val in hash_data.statements:
            self.operations.append(
                lambda h=hash_val: self._rollback_statement(h)  # type: ignore[misc]
            )

        return hash_data

    async def create_revision(
        self,
        entity_id: str,
        request_data: PreparedRequestData,
        entity_type: Any,
        edit_headers: EditHeaders,
        hash_result: StatementHashResult,
    ) -> EntityResponse:
        """Create revision using new architecture components."""
        logger.debug(f"[UpdateTransaction] Starting revision creation for {entity_id}")

        logger.debug("Importing hash service and revision components")
        from models.rest_api.entitybase.v1.services.hash_service import HashService
        from models.data.infrastructure.s3.enums import EditType, EditData
        import json
        from models.internal_representation.metadata_extractor import MetadataExtractor
        from models.data.infrastructure.s3.revision_data import S3RevisionData
        from models.data.infrastructure.s3.hashes.hash_maps import HashMaps
        from models.data.infrastructure.s3.hashes.statements_hashes import (
            StatementsHashes,
        )
        from models.infrastructure.s3.revision.revision_data import RevisionData
        from models.config.settings import settings

        logger.debug("Getting head revision ID")
        head_revision_id = self.state.vitess_client.get_head(entity_id)
        new_revision_id = head_revision_id + 1 if head_revision_id else 1
        logger.debug(f"New revision ID: {new_revision_id}")

        logger.debug("Hashing terms")
        hs = HashService(state=self.state)
        sitelink_hashes = hs.hash_sitelinks(request_data.sitelinks)
        labels_hashes = hs.hash_labels(request_data.labels)
        descriptions_hashes = hs.hash_descriptions(request_data.descriptions)
        aliases_hashes = hs.hash_aliases(request_data.aliases)

        created_at = datetime.now(timezone.utc).isoformat()

        logger.debug("Creating RevisionData object")
        # noinspection PyArgumentList
        revision_data = RevisionData(
            revision_id=new_revision_id,
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
            lemmas=request_data.lemmas,
            forms=assign_form_ids(entity_id, request_data.forms),
            senses=assign_sense_ids(entity_id, request_data.senses),
            language=request_data.language,
            lexical_category=request_data.lexical_category,
        )

        revision_dict = revision_data.model_dump(mode="json")
        revision_json = json.dumps(revision_dict, sort_keys=True)
        content_hash = MetadataExtractor.hash_string(revision_json)

        logger.debug(
            f"[UpdateTransaction.create_revision] entity_id={entity_id}, vitess_client={id(self.state.vitess_client)}, id_resolver={id(self.state.vitess_client.id_resolver)}"
        )
        self.state.vitess_client.create_revision(
            entity_id=entity_id,
            entity_data=revision_data,
            revision_id=new_revision_id,
            content_hash=content_hash,
        )

        s3_revision_data = S3RevisionData(
            schema=settings.s3_schema_revision_version,
            revision=revision_dict,
            hash=content_hash,
            created_at=created_at,
        )

        self.state.s3_client.store_revision(content_hash, s3_revision_data)

        self.operations.append(
            lambda: self._rollback_revision(entity_id, new_revision_id)
        )

        return EntityResponse(
            id=entity_id,
            rev_id=new_revision_id,
            data=s3_revision_data,
            state=EntityState(),
        )

    async def create_revision_with_hashes(
        self,
        entity_id: str,
        entity_type: Any,
        edit_headers: EditHeaders,
        existing_hashes: dict[str, Any],
        existing_revision: dict[str, Any],
    ) -> EntityResponse:
        """Create revision with pre-computed hashes (for single-term updates).

        Used by add_alias to avoid re-hashing all terms.
        """
        logger.debug(
            f"Creating revision with pre-computed hashes for entity {entity_id}"
        )
        logger.debug("Importing revision and hash components")
        from models.data.infrastructure.s3.enums import EditType, EditData
        from models.data.infrastructure.s3.hashes.hash_maps import HashMaps
        from models.data.infrastructure.s3.hashes.statements_hashes import (
            StatementsHashes,
        )
        from models.data.infrastructure.s3.hashes.labels_hashes import LabelsHashes
        from models.data.infrastructure.s3.hashes.descriptions_hashes import (
            DescriptionsHashes,
        )
        from models.data.infrastructure.s3.hashes.aliases_hashes import AliasesHashes
        from models.data.infrastructure.s3.hashes.sitelinks_hashes import SitelinkHashes
        from models.infrastructure.s3.revision.revision_data import RevisionData
        from models.data.infrastructure.s3.revision_data import S3RevisionData
        from models.config.settings import settings
        from models.internal_representation.metadata_extractor import MetadataExtractor
        import json

        logger.debug(f"Getting head revision for entity {entity_id}")
        head_revision_id = self.state.vitess_client.get_head(entity_id)
        new_revision_id = head_revision_id + 1 if head_revision_id else 1
        logger.debug(f"New revision ID: {new_revision_id}")

        created_at = datetime.now(timezone.utc).isoformat()

        logger.debug("Extracting hash data from existing_hashes")
        labels_data = existing_hashes.get("labels", {})
        descriptions_data = existing_hashes.get("descriptions", {})
        aliases_data = existing_hashes.get("aliases", {})
        sitelinks_data = existing_hashes.get("sitelinks", {})
        statements_data = existing_hashes.get("statements", {})

        logger.debug("Creating RevisionData object with pre-computed hashes")
        revision_data = RevisionData(
            revision_id=new_revision_id,
            entity_type=entity_type,
            properties=existing_revision.get("properties", []),
            property_counts=existing_revision.get("property_counts"),
            hashes=HashMaps(
                statements=StatementsHashes(root=statements_data),
                sitelinks=SitelinkHashes(root=sitelinks_data),
                labels=LabelsHashes(root=labels_data),
                descriptions=DescriptionsHashes(root=descriptions_data),
                aliases=AliasesHashes(root=aliases_data),
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
            lemmas=existing_revision.get("lemmas", {}),
            forms=existing_revision.get("forms", []),
            senses=existing_revision.get("senses", []),
            language=existing_revision.get("language", ""),
            lexical_category=existing_revision.get("lexical_category", ""),
        )

        logger.debug("Converting revision to dict and computing hash")
        revision_dict = revision_data.model_dump(mode="json")
        revision_json = json.dumps(revision_dict, sort_keys=True)
        content_hash = MetadataExtractor.hash_string(revision_json)
        logger.debug(f"Content hash: {content_hash}")

        logger.debug("Creating revision in Vitess")
        self.state.vitess_client.create_revision(
            entity_id=entity_id,
            entity_data=revision_data,
            revision_id=new_revision_id,
            content_hash=content_hash,
        )

        s3_revision_data = S3RevisionData(
            schema=settings.s3_schema_revision_version,
            revision=revision_dict,
            hash=content_hash,
            created_at=created_at,
        )

        self.state.s3_client.store_revision(content_hash, s3_revision_data)

        self.operations.append(
            lambda: self._rollback_revision(entity_id, new_revision_id)
        )

        return EntityResponse(
            id=entity_id,
            rev_id=new_revision_id,
            data=s3_revision_data,
            state=EntityState(),
        )

    def publish_event(
        self,
        event_context: EventPublishContext,
        edit_context: EditContext,
    ) -> None:
        """Publish the entity change event to the stream.

        Creates and sends an EntityChangeEvent to the configured stream producer
        for downstream processing (e.g., notifications, logging).
        """
        changed_at = event_context.changed_at
        if changed_at is None:
            changed_at = datetime.now(timezone.utc)

        logger.info(
            f"[UpdateTransaction] Starting event publishing for {event_context.entity_id}"
        )
        if self.state.entity_change_stream_producer:
            from models.infrastructure.stream.event import EntityChangeEvent

            event = EntityChangeEvent(
                id=event_context.entity_id,
                rev=event_context.revision_id,
                type=ChangeType(event_context.change_type),
                from_rev=event_context.from_revision_id,
                at=changed_at,
                user=str(edit_context.user_id),
                summary=edit_context.edit_summary,
            )
            self.state.entity_change_stream_producer.publish_change(event)
        # Events are fire-and-forget, no rollback needed

    def _rollback_statement(self, hash_val: int) -> None:
        logger.info(f"[UpdateTransaction] Rolling back statement {hash_val}")
        # Decrement ref_count
        self.state.vitess_client.decrement_ref_count(hash_val)
        # Check if orphaned and delete from S3
        ref_count = self.state.vitess_client.get_ref_count(hash_val)
        if ref_count == 0:
            self.state.s3_client.delete_statement(hash_val)

    def commit(self) -> None:
        """Commit the update transaction."""
        logger.info(f"[UpdateTransaction] Committing update for {self.entity_id}")
        self.operations.clear()
        self.lexeme_term_operations.clear()

    def rollback(self) -> None:
        """Rollback the update transaction."""
        logger.info(f"[UpdateTransaction] Rolling back update for {self.entity_id}")
        # Rollback lexeme terms first (S3 operations)
        for op in reversed(self.lexeme_term_operations):
            try:
                op()
            except Exception as e:
                logger.warning(f"[UpdateTransaction] Lexeme term rollback failed: {e}")
        # Rollback other operations (statements, revisions)
        for op in reversed(self.operations):
            try:
                op()
            except Exception as e:
                logger.warning(f"[UpdateTransaction] Rollback operation failed: {e}")
        self.lexeme_term_operations.clear()
        self.operations.clear()

    def _rollback_form_representation(self, hash_val: int) -> None:
        """Rollback form representation by deleting from S3."""
        logger.info(f"[UpdateTransaction] Rolling back form representation {hash_val}")
        try:
            self.state.s3_client._delete_metadata(
                MetadataType.FORM_REPRESENTATIONS, hash_val
            )
        except Exception as e:
            logger.warning(
                f"[UpdateTransaction] Failed to rollback form representation {hash_val}: {e}"
            )

    def _rollback_sense_gloss(self, hash_val: int) -> None:
        """Rollback sense gloss by deleting from S3."""
        logger.info(f"[UpdateTransaction] Rolling back sense gloss {hash_val}")
        try:
            self.state.s3_client._delete_metadata(MetadataType.SENSE_GLOSSES, hash_val)
        except Exception as e:
            logger.warning(
                f"[UpdateTransaction] Failed to rollback sense gloss {hash_val}: {e}"
            )

    def _rollback_lemma(self, hash_val: int) -> None:
        """Rollback lemma by deleting from S3."""
        logger.info(f"[UpdateTransaction] Rolling back lemma {hash_val}")
        try:
            self.state.s3_client._delete_metadata(MetadataType.LEMMAS, hash_val)
        except Exception as e:
            logger.warning(
                f"[UpdateTransaction] Failed to rollback lemma {hash_val}: {e}"
            )

    def _rollback_revision(self, entity_id: str, revision_id: int) -> None:
        logger.info(
            f"[UpdateTransaction] Rolling back revision {revision_id} for {entity_id}"
        )
        # Delete from entity_revisions and revert head
        self.state.vitess_client.delete_revision(entity_id, revision_id)
