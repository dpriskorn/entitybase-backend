"""Unit tests for entities endpoints."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from models.rest_api.entitybase.handlers.entity.update import EntityUpdateHandler
from models.rest_api.entitybase.handlers.entity.read import EntityReadHandler


class TestEntitiesEndpoints:
    @pytest.fixture
    def mock_clients(self):
        clients = MagicMock()
        clients.vitess = MagicMock()
        clients.s3 = MagicMock()
        clients.stream_producer = MagicMock()
        clients.validator = MagicMock()
        return clients

    @pytest.fixture
    def mock_entity_response(self):
        response = MagicMock()
        response.entity_data = {
            "type": "item",
            "labels": {},
            "sitelinks": {"enwiki": {"title": "Old Page"}}
        }
        return response

    @pytest.mark.asyncio
    async def test_put_entity_sitelinks_success(self, mock_clients, mock_entity_response):
        """Test successful sitelinks update."""
        # Mock the read handler
        with patch("models.rest_api.entitybase.versions.v1.entities.EntityReadHandler") as mock_read_class:
            mock_read_handler = MagicMock()
            mock_read_handler.get_entity.return_value = mock_entity_response
            mock_read_class.return_value = mock_read_handler

            # Mock the update handler
            with patch("models.rest_api.entitybase.versions.v1.entities.EntityUpdateHandler") as mock_update_class:
                mock_update_handler = MagicMock()
                mock_update_result = MagicMock()
                mock_update_handler.update_entity = AsyncMock(return_value=mock_update_result)
                mock_update_class.return_value = mock_update_handler

                # Import the function
                from models.rest_api.entitybase.versions.v1.entities import put_entity_sitelinks

                # Mock request
                req = MagicMock()
                req.app.state.clients = mock_clients

                # Call the function
                sitelinks_data = {"enwiki": {"title": "New Page"}, "frwiki": {"title": "PageFr"}}
                result = await put_entity_sitelinks("Q42", sitelinks_data, req)

                # Assertions
                mock_read_handler.get_entity.assert_called_once_with("Q42", mock_clients.vitess, mock_clients.s3)
                assert mock_entity_response.entity_data["sitelinks"] == sitelinks_data
                mock_update_handler.update_entity.assert_called_once()
                assert result == mock_update_result