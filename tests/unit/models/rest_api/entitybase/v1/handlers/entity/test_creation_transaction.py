"""Unit tests for CreationTransaction."""

from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timezone

import pytest

from models.data.infrastructure.s3.enums import EditType, EditData, EntityType
from models.data.infrastructure.s3.hashes.hash_maps import HashMaps
from models.data.infrastructure.s3.hashes.statements_hashes import StatementsHashes
from models.data.infrastructure.s3.entity_state import EntityState
from models.data.infrastructure.stream.change_type import ChangeType
from models.data.rest_api.v1.entitybase.request.entity import PreparedRequestData
from models.data.rest_api.v1.entitybase.request.edit_context import EditContext
from models.data.rest_api.v1.entitybase.request.entity.context import (
    EventPublishContext,
)
from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from models.data.rest_api.v1.entitybase.response import StatementHashResult
from models.rest_api.entitybase.v1.handlers.entity.creation_transaction import (
    CreationTransaction,
)
from models.config.settings import settings


class TestCreationTransaction:
    """Unit tests for CreationTransaction."""

    @pytest.mark.asyncio
    async def test_create_revision_success(self) -> None:
        """Test successful revision creation."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_s3 = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = mock_s3

        entity_id = "Q42"
        entity_type = EntityType.ITEM
        edit_headers = EditHeaders(x_user_id=123, x_edit_summary="Test creation")

        hash_result = StatementHashResult(
            statements=[1, 2, 3], properties=["P31"], property_counts={"P31": 1}
        )

        request_data = PreparedRequestData(
            id=entity_id,
            labels={"en": {"language": "en", "value": "Test"}},
            descriptions={},
            aliases={},
            sitelinks={},
            claims={},
            data={},
        )

        transaction = CreationTransaction(state=mock_state, entity_id=entity_id)

        result = await transaction.create_revision(
            entity_id=entity_id,
            request_data=request_data,
            entity_type=entity_type,
            edit_headers=edit_headers,
            hash_result=hash_result,
        )

        assert result.id == entity_id
        assert result.revision_id == 1
        assert isinstance(result.entity_data, object)

        mock_vitess.create_revision.assert_called_once()
        mock_s3.store_revision.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_revision_with_properties(self) -> None:
        """Test revision creation with multiple properties."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_s3 = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = mock_s3

        entity_id = "Q1"
        entity_type = EntityType.ITEM
        edit_headers = EditHeaders(x_user_id=1, x_edit_summary="Initial creation")

        hash_result = StatementHashResult(
            statements=[10, 20, 30],
            properties=["P31", "P279"],
            property_counts={"P31": 1, "P279": 2},
        )

        request_data = PreparedRequestData(
            id=entity_id,
            labels={},
            descriptions={},
            aliases={},
            sitelinks={},
            claims={},
            data={},
        )

        transaction = CreationTransaction(state=mock_state, entity_id=entity_id)

        result = await transaction.create_revision(
            entity_id=entity_id,
            request_data=request_data,
            entity_type=entity_type,
            edit_headers=edit_headers,
            hash_result=hash_result,
        )

        assert result.id == entity_id
        assert result.revision_id == 1

        call_args = mock_vitess.create_revision.call_args
        assert call_args[1]["entity_id"] == entity_id
        assert call_args[1]["revision_id"] == 1
        assert "properties" in call_args[1]["entity_data"].model_dump()
        assert call_args[1]["entity_data"].properties == ["P31", "P279"]

    @pytest.mark.asyncio
    @patch("models.rest_api.entitybase.v1.handlers.entity.handler.EntityHandler")
    async def test_process_statements(self, mock_entity_handler_class) -> None:
        """Test statement processing."""
        mock_state = MagicMock()
        mock_entity_handler = MagicMock()
        mock_entity_handler_class.return_value = mock_entity_handler

        hash_result = StatementHashResult(
            statements=[100, 200], properties=["P1"], property_counts={"P1": 2}
        )
        mock_entity_handler.process_statements.return_value = hash_result

        entity_id = "Q123"
        request_data = PreparedRequestData(
            id=entity_id,
            labels={},
            descriptions={},
            aliases={},
            sitelinks={},
            claims={},
            data={},
        )
        validator = MagicMock()

        transaction = CreationTransaction(state=mock_state, entity_id=entity_id)

        result = transaction.process_statements(
            entity_id=entity_id, request_data=request_data, validator=validator
        )

        assert result == hash_result
        assert len(transaction.statement_hashes) == 2
        assert len(transaction.operations) == 2

    @pytest.mark.asyncio
    async def test_publish_event(self) -> None:
        """Test event publishing."""
        mock_state = MagicMock()
        mock_producer = MagicMock()
        mock_state.entity_change_stream_producer = mock_producer

        entity_id = "Q42"
        revision_id = 1
        event_context = EventPublishContext(
            entity_id=entity_id,
            revision_id=revision_id,
            from_revision_id=0,
            change_type=ChangeType.CREATION,
            changed_at=datetime.now(timezone.utc),
        )
        edit_context = EditContext(user_id=123, edit_summary="Test creation")

        transaction = CreationTransaction(state=mock_state, entity_id=entity_id)

        transaction.publish_event(event_context, edit_context)

        mock_producer.publish_change.assert_called_once()

    def test_commit(self) -> None:
        """Test transaction commit."""
        mock_state = MagicMock()
        entity_id = "Q42"
        transaction = CreationTransaction(state=mock_state, entity_id=entity_id)

        transaction.operations.append(lambda: None)
        transaction.operations.append(lambda: None)

        assert len(transaction.operations) == 2

        transaction.commit()

        assert len(transaction.operations) == 0

    def test_rollback(self) -> None:
        """Test transaction rollback."""
        mock_state = MagicMock()
        entity_id = "Q42"
        transaction = CreationTransaction(state=mock_state, entity_id=entity_id)

        rollback_calls = []
        transaction.operations.append(lambda: rollback_calls.append(1))
        transaction.operations.append(lambda: rollback_calls.append(2))
        transaction.operations.append(lambda: rollback_calls.append(3))

        transaction.rollback()

        assert rollback_calls == [3, 2, 1]
        assert len(transaction.operations) == 0
