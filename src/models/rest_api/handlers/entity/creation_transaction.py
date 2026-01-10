from pydantic import BaseModel, Field
from abc import ABC, abstractmethod
from typing import List, Callable, Any
import logging

from models.api import StatementHashResult

logger = logging.getLogger(__name__)


class EntityTransaction(BaseModel, ABC):
    """Base class for entity transactions with shared rollback logic."""

    entity_id: str = ""
    operations: List[Callable[[], None]] = Field(default_factory=list)
    statement_hashes: List[int] = Field(default_factory=list)

    @abstractmethod
    def process_statements(
        self,
        entity_id: str,
        request_data: dict,
        vitess_client: Any,
        s3_client: Any,
        validator: Any,
    ) -> StatementHashResult:
        pass

    @abstractmethod
    async def create_revision(
        self,
        entity_id: str,
        new_revision_id: int,
        head_revision_id: int,
        request_data: dict,
        entity_type: str,
        hash_result: StatementHashResult,
        content_hash: int,
        is_mass_edit: bool,
        edit_type: Any,
        edit_summary: str,
        editor: str,
        is_semi_protected: bool,
        is_locked: bool,
        is_archived: bool,
        is_dangling: bool,
        is_mass_edit_protected: bool,
        vitess_client: Any,
        stream_producer: Any,
        is_creation: bool,
    ) -> Any:
        pass

    @abstractmethod
    def publish_event(
        self,
        entity_id: str,
        revision_id: int,
        change_type: Any,
        changed_at: Any,
        stream_producer: Any,
        from_revision_id: int = 0,
        editor: str = "",
        edit_summary: str = "",
    ) -> None:
        pass

    def commit(self) -> None:
        """Commit the transaction by clearing rollback operations."""
        logger.info("[EntityTransaction] Committing transaction")
        self.operations.clear()

    def rollback(self) -> None:
        """Rollback by executing operations in reverse."""
        logger.info("[EntityTransaction] Rolling back transaction")
        for op in reversed(self.operations):
            try:
                op()
            except Exception as e:
                logger.warning(f"[EntityTransaction] Rollback operation failed: {e}")
        self.operations.clear()

    def register_entity(self, vitess_client: Any, entity_id: str) -> None:
        logger.info(
            f"[CreationTransaction] Starting entity registration for {entity_id}"
        )
        vitess_client.register_entity(entity_id)
        self.entity_id = entity_id
        self.operations.append(
            lambda: self._rollback_entity_registration(vitess_client)
        )

    def _rollback_entity_registration(self, vitess_client: Any) -> None:
        logger.info(
            f"[CreationTransaction] Rolling back entity registration for {self.entity_id}"
        )
        # For creation, since entity is new, perhaps no action needed, or delete from id_mapping if possible
        pass


class CreationTransaction(EntityTransaction):
    """Manages atomic creation operations with rollback support."""

    def register_entity(self, vitess_client: Any, entity_id: str) -> None:
        logger.info(
            f"[CreationTransaction] Starting entity registration for {entity_id}"
        )
        vitess_client.register_entity(entity_id)
        self.entity_id = entity_id
        self.operations.append(
            lambda: self._rollback_entity_registration(vitess_client)
        )

    def process_statements(
        self,
        entity_id: str,
        request_data: dict,
        vitess_client: Any,
        s3_client: Any,
        validator: Any,
    ) -> Any:
        logger.info(
            f"[CreationTransaction] Starting statement processing for {entity_id}"
        )
        # Import here to avoid circular imports
        from . import EntityHandler

        handler = EntityHandler()
        hash_result = handler._process_statements(
            entity_id, request_data, vitess_client, s3_client, validator
        )
        # Track hashes for rollback
        self.statement_hashes.extend(hash_result.statements)
        for hash_val in hash_result.statements:
            self.operations.append(
                lambda h=hash_val: self._rollback_statement(h, vitess_client, s3_client)  # type: ignore[misc]
            )
        return hash_result

    async def create_revision(
        self,
        entity_id: str,
        new_revision_id: int,
        head_revision_id: int,
        request_data: dict,
        entity_type: str,
        hash_result: Any,
        content_hash: int,
        is_mass_edit: bool,
        edit_type: Any,
        edit_summary: str,
        editor: str,
        is_semi_protected: bool,
        is_locked: bool,
        is_archived: bool,
        is_dangling: bool,
        is_mass_edit_protected: bool,
        vitess_client: Any,
        stream_producer: Any,
        is_creation: bool,
    ) -> Any:
        logger.info(f"[CreationTransaction] Starting revision creation for {entity_id}")
        from . import EntityHandler

        handler = EntityHandler()
        response = await handler._create_and_store_revision(
            entity_id=entity_id,
            new_revision_id=new_revision_id,
            head_revision_id=head_revision_id,
            request_data=request_data,
            entity_type=entity_type,
            hash_result=hash_result,
            content_hash=content_hash,
            is_mass_edit=is_mass_edit,
            edit_type=edit_type,
            edit_summary=edit_summary,
            editor=editor,
            is_semi_protected=is_semi_protected,
            is_locked=is_locked,
            is_archived=is_archived,
            is_dangling=is_dangling,
            is_mass_edit_protected=is_mass_edit_protected,
            vitess_client=vitess_client,
            stream_producer=stream_producer,
            is_creation=is_creation,
        )
        self.operations.append(
            lambda: self._rollback_revision(entity_id, new_revision_id, vitess_client)
        )
        return response

    def publish_event(
        self,
        entity_id: str,
        revision_id: int,
        change_type: Any,
        changed_at: Any,
        stream_producer: Any,
        from_revision_id: int = 0,
        editor: str = "",
        edit_summary: str = "",
    ) -> None:
        logger.info(f"[CreationTransaction] Starting event publishing for {entity_id}")
        if stream_producer:
            from models.infrastructure.stream.producer import EntityChangeEvent

            event = EntityChangeEvent(
                entity_id=entity_id,
                revision_id=revision_id,
                change_type=change_type,
                from_revision_id=from_revision_id,
                changed_at=changed_at,
                editor=editor,
                edit_summary=edit_summary,
            )
            stream_producer.publish_change(event)
        # Events are fire-and-forget, no rollback needed

    def commit(self) -> None:
        logger.info(f"[CreationTransaction] Committing creation for {self.entity_id}")

        self.operations.clear()  # Prevent rollback after commit

    def rollback(self) -> None:
        logger.info(f"[CreationTransaction] Rolling back creation for {self.entity_id}")
        for op in reversed(self.operations):
            try:
                op()
            except Exception as e:
                logger.warning(f"[CreationTransaction] Rollback operation failed: {e}")
        self.operations.clear()

    # Private rollback methods
    def _rollback_entity_registration(self, vitess_client: Any) -> None:
        logger.info(
            f"[CreationTransaction] Rolling back entity registration for {self.entity_id}"
        )
        # TODO: Delete from entity_id_mapping if possible
        # Since register_entity just inserts, and we assume no conflicts, perhaps no action needed
        pass

    def _rollback_statement(
        self, hash_val: int, vitess_client: Any, s3_client: Any
    ) -> None:
        logger.info(f"[CreationTransaction] Rolling back statement {hash_val}")
        # Decrement ref_count
        vitess_client.decrement_ref_count(hash_val)
        # Check if orphaned and delete from S3
        ref_count = vitess_client.get_ref_count(hash_val)
        if ref_count == 0:
            s3_client.delete_statement(hash_val)

    def _rollback_revision(
        self, entity_id: str, revision_id: int, vitess_client: Any
    ) -> None:
        logger.info(
            f"[CreationTransaction] Rolling back revision {revision_id} for {entity_id}"
        )
        # Delete from entity_revisions and entity_head
        vitess_client.delete_revision(entity_id, revision_id)
        # S3 deletion if needed, but assume Vitess handles it or add s3_client.delete_revision
