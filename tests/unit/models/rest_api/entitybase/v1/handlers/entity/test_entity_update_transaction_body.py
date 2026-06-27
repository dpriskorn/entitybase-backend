"""Unit tests for EntityUpdateHandler._update_with_transaction body."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from models.data.infrastructure.s3.enums import EntityType
from models.data.rest_api.v1.entitybase.request.headers import EditHeaders
from models.infrastructure.s3.exceptions import S3NotFoundError
from models.rest_api.entitybase.v1.handlers.entity.update import EntityUpdateHandler


class TestEntityUpdateTransactionBody:
    """Tests for _update_with_transaction method body."""

    @pytest.mark.asyncio
    async def test_update_with_transaction_s3_not_found(self) -> None:
        """Test update when S3 revision not found during processing."""
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_s3 = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_state.s3_client = mock_s3
        mock_state.entity_change_stream_producer = AsyncMock()

        mock_mysql.entity_exists.return_value = True
        mock_mysql.is_entity_deleted.return_value = False
        mock_mysql.is_entity_locked.return_value = False
        mock_mysql.get_head.return_value = 2

        handler = EntityUpdateHandler(state=mock_state)
        modified_data = {"labels": {"en": {"language": "en", "value": "Test"}}}

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.update.UpdateTransaction"
        ) as mock_tx_cls:
            mock_tx = MagicMock()
            mock_tx_cls.return_value = mock_tx
            mock_tx.state = mock_state
            mock_tx.process_statements.side_effect = S3NotFoundError(
                "Revision not found"
            )

            with pytest.raises(HTTPException) as exc_info:
                await handler._update_with_transaction(
                    "Q42",
                    modified_data,
                    EntityType.ITEM,
                    EditHeaders(x_edit_summary="Update"),
                )
            assert exc_info.value.status_code == 404
            mock_tx.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_with_transaction_http_exception(self) -> None:
        """Test update when an HTTPException is raised during processing."""
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_s3 = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_state.s3_client = mock_s3
        mock_state.entity_change_stream_producer = AsyncMock()

        mock_mysql.entity_exists.return_value = True
        mock_mysql.is_entity_deleted.return_value = False
        mock_mysql.is_entity_locked.return_value = False
        mock_mysql.get_head.return_value = 2

        handler = EntityUpdateHandler(state=mock_state)
        modified_data = {"labels": {"en": {"language": "en", "value": "Test"}}}

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.update.UpdateTransaction"
        ) as mock_tx_cls:
            mock_tx = MagicMock()
            mock_tx_cls.return_value = mock_tx
            mock_tx.state = mock_state
            mock_tx.process_statements.side_effect = HTTPException(
                status_code=422, detail="Validation failed"
            )

            with pytest.raises(HTTPException) as exc_info:
                await handler._update_with_transaction(
                    "Q42",
                    modified_data,
                    EntityType.ITEM,
                    EditHeaders(x_edit_summary="Update"),
                )
            assert exc_info.value.status_code == 422
            mock_tx.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_with_transaction_generic_exception(self) -> None:
        """Test update when a generic exception is raised during processing."""
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_s3 = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_state.s3_client = mock_s3
        mock_state.entity_change_stream_producer = AsyncMock()

        mock_mysql.entity_exists.return_value = True
        mock_mysql.is_entity_deleted.return_value = False
        mock_mysql.is_entity_locked.return_value = False
        mock_mysql.get_head.return_value = 2

        handler = EntityUpdateHandler(state=mock_state)
        modified_data = {"labels": {"en": {"language": "en", "value": "Test"}}}

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.update.UpdateTransaction"
        ) as mock_tx_cls:
            mock_tx = MagicMock()
            mock_tx_cls.return_value = mock_tx
            mock_tx.state = mock_state
            mock_tx.process_statements.side_effect = Exception("Unexpected error")

            with pytest.raises(HTTPException) as exc_info:
                await handler._update_with_transaction(
                    "Q42",
                    modified_data,
                    EntityType.ITEM,
                    EditHeaders(x_edit_summary="Update"),
                )
            assert exc_info.value.status_code == 500
            assert "Unexpected error" in str(exc_info.value.detail)
            mock_tx.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_with_transaction_full_success(self) -> None:
        """Test successful update with full execution of _update_with_transaction body."""
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_s3 = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_state.s3_client = mock_s3
        mock_state.entity_change_stream_producer = AsyncMock()

        mock_mysql.entity_exists.return_value = True
        mock_mysql.is_entity_deleted.return_value = False
        mock_mysql.is_entity_locked.return_value = False
        mock_mysql.get_head.return_value = 2

        handler = EntityUpdateHandler(state=mock_state)
        modified_data = {"labels": {"en": {"language": "en", "value": "Test"}}}

        from models.data.rest_api.v1.entitybase.response import (
            EntityResponse,
            StatementHashResult,
        )
        from models.data.infrastructure.s3.revision_data import S3RevisionData

        s3_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={
                "id": "Q42",
                "labels": {"en": {"language": "en", "value": "Test"}},
                "state": {
                    "is_semi_protected": False,
                    "is_locked": False,
                    "is_archived": False,
                    "is_dangling": True,
                    "is_mass_edit_protected": False,
                },
            },
            hash=12345,
            created_at="2023-01-01T12:00:00Z",
        )

        mock_response = EntityResponse(
            id="Q42",
            rev_id=3,
            data=s3_revision_data,
        )

        hash_result = StatementHashResult(
            statements=[111, 222],
            properties=["P31"],
            property_counts={"P31": 2},
        )

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.update.UpdateTransaction"
        ) as mock_tx_cls:
            mock_tx = MagicMock()
            mock_tx_cls.return_value = mock_tx
            mock_tx.state = mock_state
            mock_tx.entity_id = "Q42"
            mock_tx.process_statements.return_value = hash_result
            mock_tx.create_revision = AsyncMock(return_value=mock_response)
            mock_tx.publish_event = AsyncMock()
            mock_mysql.user_repository.log_user_activity = AsyncMock(
                return_value=MagicMock(success=True)
            )

            result = await handler._update_with_transaction(
                "Q42",
                modified_data,
                EntityType.ITEM,
                EditHeaders(x_edit_summary="Update"),
                user_id=123,
            )

            assert result.id == "Q42"
            assert result.revision_id == 3
            mock_tx.process_statements.assert_called_once()
            mock_tx.create_revision.assert_called_once()
            mock_tx.publish_event.assert_called_once()
            mock_tx.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_with_transaction_user_activity_failure(self) -> None:
        """Test update handles user activity logging failure gracefully."""
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_s3 = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_state.s3_client = mock_s3
        mock_state.entity_change_stream_producer = AsyncMock()

        mock_mysql.entity_exists.return_value = True
        mock_mysql.is_entity_deleted.return_value = False
        mock_mysql.is_entity_locked.return_value = False
        mock_mysql.get_head.return_value = 2

        handler = EntityUpdateHandler(state=mock_state)
        modified_data = {"labels": {"en": {"language": "en", "value": "Test"}}}

        from models.data.rest_api.v1.entitybase.response import (
            EntityResponse,
            StatementHashResult,
        )
        from models.data.infrastructure.s3.revision_data import S3RevisionData

        s3_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={
                "id": "Q42",
                "labels": {"en": {"language": "en", "value": "Test"}},
            },
            hash=12345,
            created_at="2023-01-01T12:00:00Z",
        )
        mock_response = EntityResponse(
            id="Q42",
            rev_id=3,
            data=s3_revision_data,
        )

        hash_result = StatementHashResult(
            statements=[111],
            properties=["P31"],
            property_counts={"P31": 1},
        )

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.update.UpdateTransaction"
        ) as mock_tx_cls:
            mock_tx = MagicMock()
            mock_tx_cls.return_value = mock_tx
            mock_tx.state = mock_state
            mock_tx.entity_id = "Q42"
            mock_tx.process_statements.return_value = hash_result
            mock_tx.create_revision = AsyncMock(return_value=mock_response)
            mock_tx.publish_event = AsyncMock()
            mock_mysql.user_repository.log_user_activity = AsyncMock(
                return_value=MagicMock(success=False, error="DB error")
            )

            result = await handler._update_with_transaction(
                "Q42",
                modified_data,
                EntityType.ITEM,
                EditHeaders(x_edit_summary="Update"),
                user_id=123,
            )

            assert result.id == "Q42"
            mock_tx.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_with_transaction_no_user_id(self) -> None:
        """Test update when user_id is 0 (skips activity logging)."""
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_s3 = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_state.s3_client = mock_s3
        mock_state.entity_change_stream_producer = AsyncMock()

        mock_mysql.entity_exists.return_value = True
        mock_mysql.is_entity_deleted.return_value = False
        mock_mysql.is_entity_locked.return_value = False
        mock_mysql.get_head.return_value = 2

        handler = EntityUpdateHandler(state=mock_state)
        modified_data = {"labels": {"en": {"language": "en", "value": "Test"}}}

        from models.data.rest_api.v1.entitybase.response import (
            EntityResponse,
            StatementHashResult,
        )
        from models.data.infrastructure.s3.revision_data import S3RevisionData

        s3_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={
                "id": "Q42",
                "labels": {"en": {"language": "en", "value": "Test"}},
            },
            hash=12345,
            created_at="2023-01-01T12:00:00Z",
        )
        mock_response = EntityResponse(
            id="Q42",
            rev_id=3,
            data=s3_revision_data,
        )

        hash_result = StatementHashResult(
            statements=[111],
            properties=["P31"],
            property_counts={"P31": 1},
        )

        with patch(
            "models.rest_api.entitybase.v1.handlers.entity.update.UpdateTransaction"
        ) as mock_tx_cls:
            mock_tx = MagicMock()
            mock_tx_cls.return_value = mock_tx
            mock_tx.state = mock_state
            mock_tx.entity_id = "Q42"
            mock_tx.process_statements.return_value = hash_result
            mock_tx.create_revision = AsyncMock(return_value=mock_response)
            mock_tx.publish_event = AsyncMock()

            result = await handler._update_with_transaction(
                "Q42",
                modified_data,
                EntityType.ITEM,
                EditHeaders(x_edit_summary="Bot update"),
                user_id=0,
            )

            assert result.id == "Q42"
            mock_mysql.user_repository.log_user_activity.assert_not_called()
