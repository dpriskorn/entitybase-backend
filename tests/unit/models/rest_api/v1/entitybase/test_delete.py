"""Unit tests for EntityDeleteHandler."""

from unittest.mock import MagicMock

import pytest

from models.infrastructure.s3.enums import DeleteType
from models.rest_api.v1.entitybase.handlers.entity.delete import EntityDeleteHandler
from models.rest_api.v1.entitybase.request.entity import EntityDeleteRequest
from models.rest_api.v1.entitybase.response import EntityDeleteResponse


class TestEntityDeleteHandler:
    @pytest.fixture
    def handler(self):
        return EntityDeleteHandler()

    @pytest.fixture
    def mock_vitess_client(self):
        return MagicMock()

    @pytest.fixture
    def mock_s3_client(self):
        return MagicMock()

    @pytest.fixture
    def mock_stream_producer(self):
        return MagicMock()

    @pytest.fixture
    def delete_request(self):
        return EntityDeleteRequest(
            entity_id="Q123",
            delete_type=DeleteType.SOFT,
            edit_summary="Test delete",
            tags=[],
        )

    @pytest.mark.asyncio
    async def test_delete_entity_soft_delete_success(
        self,
        handler,
        mock_vitess_client,
        mock_s3_client,
        mock_stream_producer,
        delete_request,
    ):
        """Test successful soft delete."""
        mock_vitess_client.entity_exists.return_value = True
        mock_vitess_client.get_head.return_value = 100
        mock_vitess_client.create_revision.return_value = 101

        response = await handler.delete_entity(
            "Q42",
            delete_request,
            mock_vitess_client,
            mock_s3_client,
            mock_stream_producer,
            user_id=123,
        )

        assert isinstance(response, EntityDeleteResponse)
        assert response.revision_id == 101
        mock_vitess_client.create_revision.assert_called_once()
        mock_stream_producer.send_entity_change_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_entity_hard_delete_success(
        self, handler, mock_vitess_client, mock_s3_client, mock_stream_producer
    ):
        """Test successful hard delete."""
        request = EntityDeleteRequest(
            delete_type=DeleteType.HARD,
            edit_summary="Hard delete",
            tags=[],
        )

        mock_vitess_client.entity_exists.return_value = True
        mock_vitess_client.get_head.return_value = 100
        mock_vitess_client.create_revision.return_value = 101

        response = await handler.delete_entity(
            "Q42",
            request,
            mock_vitess_client,
            mock_s3_client,
            mock_stream_producer,
            user_id=123,
        )

        assert isinstance(response, EntityDeleteResponse)
        assert response.revision_id == 101
        mock_vitess_client.create_revision.assert_called_once()
        mock_vitess_client.delete_entity.assert_called_once()
        mock_stream_producer.send_entity_change_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_entity_not_found(
        self, handler, mock_vitess_client, mock_s3_client, mock_stream_producer, request
    ):
        """Test delete entity when entity not found."""
        mock_vitess_client.entity_exists.return_value = False

        with pytest.raises(Exception):  # raise_validation_error
            await handler.delete_entity(
                "Q42",
                request,
                mock_vitess_client,
                mock_s3_client,
                mock_stream_producer,
                user_id=123,
            )

    @pytest.mark.asyncio
    async def test_delete_entity_vitess_none(
        self, handler, mock_s3_client, mock_stream_producer, request
    ):
        """Test delete entity when vitess client is None."""
        with pytest.raises(Exception):  # raise_validation_error
            await handler.delete_entity(
                "Q42", request, None, mock_s3_client, mock_stream_producer, user_id=123
            )

    @pytest.mark.asyncio
    async def test_delete_entity_s3_none(
        self, handler, mock_vitess_client, mock_stream_producer, request
    ):
        """Test delete entity when S3 client is None."""
        with pytest.raises(Exception):  # raise_validation_error
            await handler.delete_entity(
                "Q42",
                request,
                mock_vitess_client,
                None,
                mock_stream_producer,
                user_id=123,
            )

    @pytest.mark.asyncio
    async def test_delete_entity_stream_event_failure(
        self, handler, mock_vitess_client, mock_s3_client, mock_stream_producer, request
    ):
        """Test delete entity when stream event fails."""
        mock_vitess_client.entity_exists.return_value = True
        mock_vitess_client.get_head.return_value = 100
        mock_vitess_client.create_entity_revision.return_value = 101
        mock_stream_producer.send_entity_change_event.side_effect = Exception(
            "Stream error"
        )

        # Should still succeed as stream failure is logged but not raised
        response = await handler.delete_entity(
            "Q42",
            request,
            mock_vitess_client,
            mock_s3_client,
            mock_stream_producer,
            user_id=123,
        )

        assert isinstance(response, EntityDeleteResponse)
        mock_stream_producer.send_entity_change_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_entity_user_activity_logging(
        self, handler, mock_vitess_client, mock_s3_client, mock_stream_producer, request
    ):
        """Test user activity logging on delete."""
        mock_vitess_client.entity_exists.return_value = True
        mock_vitess_client.get_head.return_value = 100
        mock_vitess_client.create_entity_revision.return_value = 101

        await handler.delete_entity(
            "Q42",
            request,
            mock_vitess_client,
            mock_s3_client,
            mock_stream_producer,
            user_id=123,
        )

        # Verify activity logging was called
        mock_vitess_client.user_repository.log_user_activity.assert_called_once_with(
            user_id=123, activity_type="entity_delete", entity_id="Q42", revision_id=101
        )
