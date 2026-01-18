import sys
from unittest.mock import MagicMock

import pytest

pytestmark = pytest.mark.unit

sys.path.insert(0, "src")

from models.common import OperationResult
from models.rest_api.entitybase.request.entity.revert import EntityRevertRequest
from models.rest_api.entitybase.response.entity.revert import EntityRevertResponse
from models.rest_api.entitybase.handlers.entity.revert import EntityRevertHandler


class TestEntityRevertHandler:
    """Unit tests for EntityRevertHandler"""

    @pytest.fixture
    def mock_vitess_client(self) -> MagicMock:
        """Mock Vitess client"""
        client = MagicMock()
        client.id_resolver = MagicMock()
        client.revision_repository = MagicMock()
        client.head_repository = MagicMock()
        return client

    @pytest.fixture
    def handler(self) -> EntityRevertHandler:
        """Create handler instance"""
        return EntityRevertHandler()

    @pytest.mark.asyncio
    async def test_revert_entity_success(
        self, handler: EntityRevertHandler, mock_vitess_client: MagicMock
    ) -> None:
        """Test successful entity revert"""
        request = EntityRevertRequest(
            to_revision_id=123,
            reason="Vandalism",
            watchlist_context={"notification_id": 789},
        )

        # Mock resolutions
        mock_vitess_client.id_resolver.resolve_id.return_value = 1001
        mock_vitess_client.revision_repository.get_revision.return_value = {
            "statements": [],
            "properties": [],
        }
        from models.common import OperationResult

        mock_vitess_client.head_repository.get_head_revision.return_value = (
            OperationResult(success=True, data=125)
        )

        mock_s3 = MagicMock()
        mock_s3.read_full_revision.return_value = MagicMock(
            data={"entity": {"statements": [], "properties": [], "property_counts": []}}
        )
        from unittest.mock import AsyncMock

        mock_stream_producer = MagicMock()
        mock_stream_producer.publish_event = AsyncMock()

        result = await handler.revert_entity(
            "Q42", request, mock_vitess_client, mock_s3, mock_stream_producer, 456
        )

        assert isinstance(result, EntityRevertResponse)
        assert result.entity_id == "Q42"

    @pytest.mark.asyncio
    async def test_revert_entity_not_found(
        self, handler: EntityRevertHandler, mock_vitess_client: MagicMock
    ) -> None:
        """Test revert when entity not found"""
        request = EntityRevertRequest(to_revision_id=123, reason="Test")

        mock_vitess_client.id_resolver.resolve_id.return_value = 0  # Not found

        with pytest.raises(Exception):  # ValidationError
            await handler.revert_entity(
                "Q42", request, mock_vitess_client, MagicMock(), MagicMock(), 456
            )

    @pytest.mark.asyncio
    async def test_revert_entity_revision_not_found(
        self, handler: EntityRevertHandler, mock_vitess_client: MagicMock
    ) -> None:
        """Test revert when target revision not found"""
        request = EntityRevertRequest(to_revision_id=123, reason="Test")

        mock_vitess_client.id_resolver.resolve_id.return_value = 1001
        mock_vitess_client.revision_repository.get_revision.return_value = None

        with pytest.raises(Exception):  # ValidationError
            await handler.revert_entity(
                "Q42", request, mock_vitess_client, MagicMock(), MagicMock(), 456
            )

    @pytest.mark.asyncio
    async def test_revert_entity_already_at_revision(
        self, handler: EntityRevertHandler, mock_vitess_client: MagicMock
    ) -> None:
        """Test revert when already at target revision"""
        request = EntityRevertRequest(to_revision_id=123, reason="Test")

        mock_vitess_client.id_resolver.resolve_id.return_value = 1001
        mock_vitess_client.revision_repository.get_revision.return_value = {
            "statements": []
        }
        mock_vitess_client.head_repository.get_head_revision.return_value = (
            OperationResult(success=True, data=123)  # Same as target
        )

        with pytest.raises(Exception):  # ValidationError
            await handler.revert_entity(
                "Q42", request, mock_vitess_client, MagicMock(), MagicMock(), 456
            )
