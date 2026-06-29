"""Unit tests for EntityTransaction in entity_transaction.py."""

from datetime import datetime, timezone
from unittest.mock import MagicMock
import pytest

from models.data.rest_api.v1.entitybase.response import StatementHashResult
from models.rest_api.entitybase.v1.handlers.entity.entity_transaction import (
    EntityTransaction,
)


class ConcreteEntityTransaction(EntityTransaction):
    """Concrete implementation for testing."""

    def process_statements(
        self,
        entity_id: str,
        request_data,
        validator,
    ) -> StatementHashResult:
        return StatementHashResult(
            statements=[],
            labels={},
            descriptions={},
            aliases={},
            sitelinks={},
        )


class TestEntityTransactionMethods:
    """Tests for EntityTransaction methods."""

    @pytest.fixture
    def mock_state(self) -> MagicMock:
        state = MagicMock()
        state.mysql_client.entity_repository.create_entity.return_value = True
        state.mysql_client.entity_repository.delete_entity.return_value = True
        state.mysql_client.entity_repository.delete.return_value = True
        return state

    @pytest.fixture
    def tx(self, mock_state: MagicMock) -> ConcreteEntityTransaction:
        return ConcreteEntityTransaction(state=mock_state, entity_id="")

    def test_register_entity(
        self, tx: ConcreteEntityTransaction, mock_state: MagicMock
    ) -> None:
        tx.register_entity("Q42")

        assert tx.entity_id == "Q42"
        mock_state.mysql_client.entity_repository.create_entity.assert_called_once_with(
            "Q42"
        )
        assert len(tx.operations) == 1

    def test_rollback_entity_registration(
        self, tx: ConcreteEntityTransaction, mock_state: MagicMock
    ) -> None:
        tx.entity_id = "Q42"
        tx._rollback_entity_registration()

        mock_state.mysql_client.entity_repository.delete_entity.assert_called_once_with(
            "Q42"
        )

    def test_rollback_revision(
        self, tx: ConcreteEntityTransaction, mock_state: MagicMock
    ) -> None:
        tx._rollback_revision("Q42", 5)

        mock_state.mysql_client.entity_repository.delete.assert_called_once_with(
            "Q42", 5
        )

    @pytest.mark.asyncio
    async def test_publish_event_with_changed_at(
        self, tx: ConcreteEntityTransaction
    ) -> None:
        from models.data.rest_api.v1.entitybase.request.edit_context import EditContext
        from models.data.rest_api.v1.entitybase.request.entity.context import (
            EventPublishContext,
        )

        event_ctx = EventPublishContext(
            entity_id="Q42",
            revision_id=5,
            change_type="edit",
            from_revision_id=4,
            changed_at=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        )
        edit_ctx = EditContext(user_id=123, edit_summary="test edit")

        await tx.publish_event(event_ctx, edit_ctx)

    @pytest.mark.asyncio
    async def test_publish_event_without_changed_at(
        self, tx: ConcreteEntityTransaction
    ) -> None:
        from models.data.rest_api.v1.entitybase.request.edit_context import EditContext
        from models.data.rest_api.v1.entitybase.request.entity.context import (
            EventPublishContext,
        )

        event_ctx = EventPublishContext(
            entity_id="Q42",
            revision_id=5,
            change_type="edit",
            from_revision_id=4,
            changed_at=None,
        )
        edit_ctx = EditContext(user_id=123, edit_summary="test edit")

        await tx.publish_event(event_ctx, edit_ctx)
