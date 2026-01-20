from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from models.rest_api.state import State

pytestmark = pytest.mark.unit

from models.rest_api.entitybase.v1.handlers.entity.backlinks import BacklinkHandler
from models.rest_api.entitybase.v1.response.entity.backlinks import BacklinkResponse


class TestBacklinkHandler:
    @pytest.fixture
    def mock_vitess(self) -> MagicMock:
        """Mock Vitess client"""
        client = MagicMock()
        client.id_resolver = MagicMock()
        client.get_backlinks = MagicMock()
        return client

    @pytest.fixture
    def handler(self, mock_vitess: MagicMock) -> BacklinkHandler:
        """Create handler instance"""
        state = MagicMock()
        state.vitess_client = mock_vitess
        return BacklinkHandler(state=state)

    @pytest.mark.asyncio
    async def test_get_backlinks_success(self, handler: BacklinkHandler, mock_vitess: MagicMock):
        """Test successful backlinks retrieval."""
        # Mock vitess client
        mock_vitess.id_resolver.resolve_id.return_value = 123
        mock_vitess.id_resolver.resolve_entity_id.return_value = "Q456"

        # Mock backlinks
        mock_backlink = MagicMock()
        mock_backlink.referencing_internal_id = 456
        mock_backlink.property_id = "P31"
        mock_backlink.rank = "normal"
        mock_vitess.get_backlinks.return_value = [mock_backlink]

        result = await handler.get("Q123", limit=50, offset=10)

        assert len(result.backlinks) == 1
        backlink = result.backlinks[0]
        assert isinstance(backlink, BacklinkResponse)
        assert backlink.entity_id == "Q456"
        assert backlink.property_id == "P31"
        assert backlink.rank == "normal"
        assert result.limit == 50
        assert result.offset == 10

    @pytest.mark.asyncio
    async def test_get_backlinks_entity_not_found(self, handler: BacklinkHandler, mock_vitess: MagicMock):
        """Test backlinks retrieval for non-existent entity."""
        mock_vitess.id_resolver.resolve_id.return_value = 0  # Not found

        with pytest.raises(HTTPException) as exc_info:
            await handler.get("Q999")

        assert exc_info.value.status_code == 404
        assert "Entity not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_backlinks_no_backlinks(self, handler: BacklinkHandler, mock_vitess: MagicMock):
        """Test backlinks retrieval with no backlinks."""
        mock_vitess.id_resolver.resolve_id.return_value = 123
        mock_vitess.get_backlinks.return_value = []

        result = await handler.get("Q123")

        assert result.backlinks == []
        assert result.limit == 100
        assert result.offset == 0

    @pytest.mark.asyncio
    async def test_get_backlinks_resolve_entity_id_failure(self, handler: BacklinkHandler, mock_vitess: MagicMock):
        """Test backlinks when entity ID resolution fails."""
        mock_vitess.id_resolver.resolve_id.return_value = 123
        mock_vitess.id_resolver.resolve_entity_id.return_value = ""  # Resolution failed

        mock_backlink = MagicMock()
        mock_backlink.referencing_internal_id = 456
        mock_backlink.property_id = "P31"
        mock_backlink.rank = "normal"
        mock_vitess.get_backlinks.return_value = [mock_backlink]

        result = await handler.get("Q123")

        # Should skip the backlink with failed resolution
        assert result.backlinks == []