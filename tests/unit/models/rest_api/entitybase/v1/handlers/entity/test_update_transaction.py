"""Unit tests for UpdateTransaction."""

from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timezone

import pytest

from models.data.infrastructure.s3.enums import EditType, EditData, EntityType
from models.data.infrastructure.s3.hashes.hash_maps import HashMaps
from models.data.infrastructure.s3.hashes.statements_hashes import StatementsHashes
from models.data.infrastructure.s3.entity_state import EntityState
from models.data.infrastructure.stream.change_type import ChangeType
from models.data.common import OperationResult
from models.data.rest_api.v1.entitybase.request.entity import PreparedRequestData
from models.data.rest_api.v1.entitybase.request.edit_context import EditContext
from models.data.rest_api.v1.entitybase.request.entity.context import (
    EventPublishContext,
)
from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from models.data.rest_api.v1.entitybase.response import StatementHashResult
from fastapi import HTTPException
from models.rest_api.entitybase.v1.handlers.entity.update_transaction import (
    UpdateTransaction,
)
from models.config.settings import settings


class TestUpdateTransaction:
    """Unit tests for UpdateTransaction."""

    @pytest.mark.asyncio
    async def test_create_revision_success(self) -> None:
        """Test successful revision creation for update."""
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_s3 = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_state.s3_client = mock_s3
        mock_mysql.get_head.return_value = 1

        entity_id = "Q42"
        entity_type = EntityType.ITEM
        edit_headers = EditHeaders(x_user_id=123, x_edit_summary="Test update")

        hash_result = StatementHashResult(
            statements=[1, 2, 3], properties=["P31"], property_counts={"P31": 1}
        )

        request_data = PreparedRequestData(
            id=entity_id,
            labels={"en": {"language": "en", "value": "Updated"}},
            descriptions={},
            aliases={},
            sitelinks={},
            claims={},
            data={},
        )

        transaction = UpdateTransaction(state=mock_state, entity_id=entity_id)

        result = await transaction.create_revision(
            entity_id=entity_id,
            request_data=request_data,
            entity_type=entity_type,
            edit_headers=edit_headers,
            hash_result=hash_result,
        )

        assert result.id == entity_id
        assert result.revision_id == 2
        assert isinstance(result.entity_data, object)

        mock_mysql.create_revision.assert_called_once()
        mock_s3.store_revision.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_revision_with_properties(self) -> None:
        """Test revision creation with multiple properties for update."""
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_s3 = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_state.s3_client = mock_s3
        mock_mysql.get_head.return_value = 1

        entity_id = "Q1"
        entity_type = EntityType.ITEM
        edit_headers = EditHeaders(x_user_id=1, x_edit_summary="Update properties")

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

        transaction = UpdateTransaction(state=mock_state, entity_id=entity_id)

        result = await transaction.create_revision(
            entity_id=entity_id,
            request_data=request_data,
            entity_type=entity_type,
            edit_headers=edit_headers,
            hash_result=hash_result,
        )

        assert result.id == entity_id
        assert result.revision_id == 2

        call_args = mock_mysql.create_revision.call_args
        assert call_args[1]["entity_id"] == entity_id
        assert call_args[1]["revision_id"] == 2
        assert "properties" in call_args[1]["entity_data"].model_dump()
        assert call_args[1]["entity_data"].properties == ["P31", "P279"]

    @pytest.mark.asyncio
    @patch(
        "models.rest_api.entitybase.v1.handlers.entity.update_transaction.StatementService"
    )
    async def test_process_statements(self, mock_statement_service_class) -> None:
        """Test statement processing for update."""
        mock_state = MagicMock()
        mock_statement_service = MagicMock()
        mock_statement_service_class.return_value = mock_statement_service

        hash_result = StatementHashResult(
            statements=[100, 200], properties=["P1"], property_counts={"P1": 2}
        )

        mock_hash_result = OperationResult[StatementHashResult](
            success=True, data=hash_result
        )
        mock_statement_service.hash_entity_statements.return_value = mock_hash_result

        mock_store_result = OperationResult(success=True, data=None)
        mock_statement_service.deduplicate_and_store_statements.return_value = (
            mock_store_result
        )

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

        transaction = UpdateTransaction(state=mock_state, entity_id=entity_id)

        result = transaction.process_statements(
            entity_id=entity_id, request_data=request_data, validator=validator
        )

        assert result == hash_result
        assert len(transaction.statement_hashes) == 2
        assert len(transaction.operations) == 2

    @pytest.mark.asyncio
    async def test_publish_event(self) -> None:
        """Test event publishing for update."""
        mock_state = MagicMock()
        mock_producer = MagicMock()
        mock_producer.publish = AsyncMock()
        mock_state.entity_change_stream_producer = mock_producer

        entity_id = "Q42"
        revision_id = 2
        event_context = EventPublishContext(
            entity_id=entity_id,
            revision_id=revision_id,
            from_revision_id=1,
            change_type=ChangeType.EDIT,
            changed_at=datetime.now(timezone.utc),
        )
        edit_context = EditContext(user_id=123, edit_summary="Test update")

        transaction = UpdateTransaction(state=mock_state, entity_id=entity_id)

        await transaction.publish_event(event_context, edit_context)

        mock_producer.publish.assert_called_once()

    def test_commit(self) -> None:
        """Test transaction commit."""
        mock_state = MagicMock()
        entity_id = "Q42"
        transaction = UpdateTransaction(state=mock_state, entity_id=entity_id)

        transaction.operations.append(lambda: None)
        transaction.operations.append(lambda: None)

        assert len(transaction.operations) == 2

        transaction.commit()

        assert len(transaction.operations) == 0

    def test_rollback(self) -> None:
        """Test transaction rollback."""
        mock_state = MagicMock()
        entity_id = "Q42"
        transaction = UpdateTransaction(state=mock_state, entity_id=entity_id)

        rollback_calls = []
        transaction.operations.append(lambda: rollback_calls.append(1))
        transaction.operations.append(lambda: rollback_calls.append(2))
        transaction.operations.append(lambda: rollback_calls.append(3))

        transaction.rollback()

        assert rollback_calls == [3, 2, 1]
        assert len(transaction.operations) == 0

    def test_rollback_with_lexeme_operations(self) -> None:
        """Test rollback processes lexeme term operations first."""
        mock_state = MagicMock()
        entity_id = "Q42"
        transaction = UpdateTransaction(state=mock_state, entity_id=entity_id)

        calls = []
        transaction.lexeme_term_operations.append(lambda: calls.append("L1"))
        transaction.operations.append(lambda: calls.append("O1"))

        transaction.rollback()

        assert calls == ["L1", "O1"]

    def test_rollback_with_exceptions(self) -> None:
        """Test rollback handles exceptions gracefully."""
        mock_state = MagicMock()
        entity_id = "Q42"
        transaction = UpdateTransaction(state=mock_state, entity_id=entity_id)

        calls = []
        transaction.lexeme_term_operations.append(
            lambda: (_ for _ in ()).throw(Exception("fail"))
        )
        transaction.lexeme_term_operations.append(lambda: calls.append("L2"))
        transaction.operations.append(lambda: (_ for _ in ()).throw(Exception("fail2")))
        transaction.operations.append(lambda: calls.append("O2"))

        transaction.rollback()

        assert calls == ["L2", "O2"]

    @pytest.mark.asyncio
    async def test_process_statements_hash_failure(self) -> None:
        """Test statement processing when hashing fails."""
        mock_state = MagicMock()
        mock_statement_service = MagicMock()
        mock_hash_result = OperationResult[StatementHashResult](
            success=False, error="Hash failed"
        )
        mock_statement_service.hash_entity_statements.return_value = mock_hash_result

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.update_transaction.StatementService",
            return_value=mock_statement_service,
        ):
            from models.rest_api.utils import raise_validation_error

            entity_id = "Q1"
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
            transaction = UpdateTransaction(state=mock_state, entity_id=entity_id)

            with pytest.raises(HTTPException) as exc_info:
                transaction.process_statements(
                    entity_id=entity_id, request_data=request_data, validator=validator
                )

            assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_process_statements_store_failure(self) -> None:
        """Test statement processing when storing fails."""
        mock_state = MagicMock()
        mock_statement_service = MagicMock()

        hash_result = StatementHashResult(
            statements=[100], properties=["P1"], property_counts={"P1": 1}
        )
        mock_hash_result = OperationResult[StatementHashResult](
            success=True, data=hash_result
        )
        mock_statement_service.hash_entity_statements.return_value = mock_hash_result

        mock_store_result = OperationResult(success=False, error="Store failed")
        mock_statement_service.deduplicate_and_store_statements.return_value = (
            mock_store_result
        )

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.update_transaction.StatementService",
            return_value=mock_statement_service,
        ):
            entity_id = "Q1"
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
            transaction = UpdateTransaction(state=mock_state, entity_id=entity_id)

            with pytest.raises(HTTPException) as exc_info:
                transaction.process_statements(
                    entity_id=entity_id, request_data=request_data, validator=validator
                )

            assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_create_revision_conflict(self) -> None:
        """Test create_revision when CAS fails."""
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_s3 = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_state.s3_client = mock_s3
        mock_mysql.get_head.return_value = 1

        entity_id = "Q42"
        entity_type = EntityType.ITEM
        edit_headers = EditHeaders(
            x_user_id=123, x_edit_summary="Test", x_base_revision_id=1
        )

        hash_result = StatementHashResult(
            statements=[1, 2, 3], properties=["P31"], property_counts={"P31": 1}
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

        transaction = UpdateTransaction(state=mock_state, entity_id=entity_id)

        mock_mysql.create_revision.return_value = False
        mock_mysql.get_head.return_value = 2

        with pytest.raises(HTTPException) as exc_info:
            await transaction.create_revision(
                entity_id=entity_id,
                request_data=request_data,
                entity_type=entity_type,
                edit_headers=edit_headers,
                hash_result=hash_result,
            )

        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_create_revision_with_hashes_success(self) -> None:
        """Test create_revision_with_hashes success."""
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_s3 = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_state.s3_client = mock_s3
        mock_mysql.get_head.return_value = 3

        entity_id = "Q1"
        entity_type = EntityType.ITEM
        edit_headers = EditHeaders(x_user_id=1, x_edit_summary="Single term update")

        existing_hashes: dict[str, Any] = {
            "labels": {},
            "descriptions": {},
            "aliases": {},
            "sitelinks": {},
            "statements": [],
        }
        existing_revision: dict[str, Any] = {
            "properties": ["P31"],
            "property_counts": {"P31": 1},
            "lemmas": {},
            "forms": [],
            "senses": [],
            "language": "",
            "lexical_category": "",
        }

        mock_mysql.create_revision.return_value = True

        transaction = UpdateTransaction(state=mock_state, entity_id=entity_id)

        result = await transaction.create_revision_with_hashes(
            entity_id=entity_id,
            entity_type=entity_type,
            edit_headers=edit_headers,
            existing_hashes=existing_hashes,
            existing_revision=existing_revision,
        )

        assert result.id == entity_id
        assert result.revision_id == 4

    @pytest.mark.asyncio
    async def test_create_revision_with_hashes_conflict(self) -> None:
        """Test create_revision_with_hashes when CAS fails."""
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_s3 = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_state.s3_client = mock_s3
        mock_mysql.get_head.return_value = 3

        entity_id = "Q1"
        entity_type = EntityType.ITEM
        edit_headers = EditHeaders(
            x_user_id=1, x_edit_summary="Test", x_base_revision_id=3
        )

        existing_hashes: dict[str, Any] = {
            "labels": {},
            "descriptions": {},
            "aliases": {},
            "sitelinks": {},
            "statements": [],
        }
        existing_revision: dict[str, Any] = {
            "properties": [],
            "property_counts": {},
            "lemmas": {},
            "forms": [],
            "senses": [],
            "language": "",
            "lexical_category": "",
        }

        mock_mysql.create_revision.return_value = False
        mock_mysql.get_head.return_value = 4

        transaction = UpdateTransaction(state=mock_state, entity_id=entity_id)

        with pytest.raises(HTTPException) as exc_info:
            await transaction.create_revision_with_hashes(
                entity_id=entity_id,
                entity_type=entity_type,
                edit_headers=edit_headers,
                existing_hashes=existing_hashes,
                existing_revision=existing_revision,
            )

        assert exc_info.value.status_code == 409

    @pytest.mark.asyncio
    async def test_publish_event_no_producer(self) -> None:
        """Test event publishing when no stream producer."""
        mock_state = MagicMock()
        mock_state.entity_change_stream_producer = None

        entity_id = "Q42"
        event_context = EventPublishContext(
            entity_id=entity_id,
            revision_id=2,
            from_revision_id=1,
            change_type=ChangeType.EDIT,
            changed_at=datetime.now(timezone.utc),
        )
        edit_context = EditContext(user_id=123, edit_summary="Test")

        transaction = UpdateTransaction(state=mock_state, entity_id=entity_id)

        await transaction.publish_event(event_context, edit_context)

    @pytest.mark.asyncio
    async def test_publish_event_no_changed_at(self) -> None:
        """Test event publishing with no changed_at."""
        mock_state = MagicMock()
        mock_producer = MagicMock()
        mock_producer.publish = AsyncMock()
        mock_state.entity_change_stream_producer = mock_producer

        entity_id = "Q42"
        event_context = EventPublishContext(
            entity_id=entity_id,
            revision_id=2,
            from_revision_id=1,
            change_type=ChangeType.EDIT,
            changed_at=None,
        )
        edit_context = EditContext(user_id=123, edit_summary="Test")

        transaction = UpdateTransaction(state=mock_state, entity_id=entity_id)

        await transaction.publish_event(event_context, edit_context)

        mock_producer.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_event_streaming_disabled(self) -> None:
        """Test event publishing when streaming is disabled."""
        mock_state = MagicMock()
        mock_producer = MagicMock()
        mock_state.entity_change_stream_producer = mock_producer
        mock_state.settings.streaming_enabled = False

        entity_id = "Q42"
        event_context = EventPublishContext(
            entity_id=entity_id,
            revision_id=2,
            from_revision_id=1,
            change_type=ChangeType.EDIT,
            changed_at=datetime.now(timezone.utc),
        )
        edit_context = EditContext(user_id=123, edit_summary="Test")

        transaction = UpdateTransaction(state=mock_state, entity_id=entity_id)

        await transaction.publish_event(event_context, edit_context)

        mock_producer.publish.assert_not_called()

    def test_rollback_statement_ref_count_greater_than_zero(self) -> None:
        """Test _rollback_statement when ref_count > 0."""
        mock_state = MagicMock()
        mock_state.mysql_client.get_ref_count.return_value = 3

        transaction = UpdateTransaction(state=mock_state, entity_id="Q42")

        transaction._rollback_statement(100)

        mock_state.mysql_client.decrement_ref_count.assert_called_once_with(100)
        mock_state.mysql_client.get_ref_count.assert_called_once_with(100)
        mock_state.s3_client.delete_statement.assert_not_called()

    def test_rollback_statement_ref_count_zero(self) -> None:
        """Test _rollback_statement when ref_count reaches 0."""
        mock_state = MagicMock()
        mock_state.mysql_client.get_ref_count.return_value = 0

        transaction = UpdateTransaction(state=mock_state, entity_id="Q42")

        transaction._rollback_statement(200)

        mock_state.mysql_client.decrement_ref_count.assert_called_once_with(200)
        mock_state.s3_client.delete_statement.assert_called_once_with(200)

    def test_rollback_form_representation_success(self) -> None:
        """Test _rollback_form_representation success."""
        mock_state = MagicMock()
        transaction = UpdateTransaction(state=mock_state, entity_id="Q42")

        transaction._rollback_form_representation(123)

        mock_state.s3_client.delete_metadata.assert_called_once()

    def test_rollback_form_representation_exception(self) -> None:
        """Test _rollback_form_representation handles exception."""
        mock_state = MagicMock()
        mock_state.s3_client.delete_metadata.side_effect = Exception("Delete failed")
        transaction = UpdateTransaction(state=mock_state, entity_id="Q42")

        transaction._rollback_form_representation(123)

    def test_rollback_sense_gloss_success(self) -> None:
        """Test _rollback_sense_gloss success."""
        mock_state = MagicMock()
        transaction = UpdateTransaction(state=mock_state, entity_id="Q42")

        transaction._rollback_sense_gloss(456)

        mock_state.s3_client.delete_metadata.assert_called_once()

    def test_rollback_sense_gloss_exception(self) -> None:
        """Test _rollback_sense_gloss handles exception."""
        mock_state = MagicMock()
        mock_state.s3_client.delete_metadata.side_effect = Exception("Delete failed")
        transaction = UpdateTransaction(state=mock_state, entity_id="Q42")

        transaction._rollback_sense_gloss(456)

    def test_rollback_lemma_success(self) -> None:
        """Test _rollback_lemma success."""
        mock_state = MagicMock()
        transaction = UpdateTransaction(state=mock_state, entity_id="Q42")

        transaction._rollback_lemma(789)

        mock_state.s3_client.delete_metadata.assert_called_once()

    def test_rollback_lemma_exception(self) -> None:
        """Test _rollback_lemma handles exception."""
        mock_state = MagicMock()
        mock_state.s3_client.delete_metadata.side_effect = Exception("Delete failed")
        transaction = UpdateTransaction(state=mock_state, entity_id="Q42")

        transaction._rollback_lemma(789)

    def test_rollback_revision(self) -> None:
        """Test _rollback_revision calls delete_revision."""
        mock_state = MagicMock()
        transaction = UpdateTransaction(state=mock_state, entity_id="Q42")

        transaction._rollback_revision("Q42", 5)

        mock_state.mysql_client.delete_revision.assert_called_once_with("Q42", 5)

    @patch(
        "models.rest_api.entitybase.v1.utils.lexeme_term_processor.process_lexeme_terms"
    )
    def test_process_lexeme_terms(self, mock_process) -> None:
        """Test process_lexeme_terms success path."""
        mock_state = MagicMock()
        transaction = UpdateTransaction(state=mock_state, entity_id="Q42")

        forms: list[dict[str, Any]] = [{"representations": {"en": {"value": "test"}}}]
        senses: list[dict[str, Any]] = []
        lemmas: dict[str, dict[str, Any]] = {"en": {"value": "test"}}

        transaction.process_lexeme_terms(forms=forms, senses=senses, lemmas=lemmas)

        mock_process.assert_called_once()
        # Verify config was created with the right callbacks by invoking through mock
        config = mock_process.call_args[1]["config"]
        assert config.s3_client == mock_state.s3_client
        assert config.lemmas == lemmas
