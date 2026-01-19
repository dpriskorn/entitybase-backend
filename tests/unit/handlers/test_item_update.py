import pytest

pytestmark = pytest.mark.unit
from unittest.mock import AsyncMock, MagicMock, patch

from models.rest_api.entitybase.request.entity import EntityUpdateRequest
from models.rest_api.entitybase.response.entity import EntityResponse, EntityState
from models.rest_api.entitybase.handlers.entity.items.update import ItemUpdateHandler


class TestItemUpdateHandler:
    """Unit tests for ItemUpdateHandler"""

    @pytest.fixture
    def handler(self) -> ItemUpdateHandler:
        """Create handler instance"""
        return ItemUpdateHandler()

    @pytest.fixture
    def mock_vitess_client(self) -> MagicMock:
        """Mock vitess client"""
        client = MagicMock()
        client.entity_exists.return_value = True
        client.is_entity_deleted.return_value = False
        client.is_entity_locked.return_value = False
        return client

    @pytest.fixture
    def mock_s3_client(self) -> MagicMock:
        """Mock S3 client"""
        return MagicMock()

    @pytest.fixture
    def mock_stream_producer(self) -> AsyncMock:
        """Mock stream producer"""
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_update_item_success(
        self,
        handler: ItemUpdateHandler,
        mock_vitess_client: MagicMock,
        mock_s3_client: MagicMock,
        mock_stream_producer: AsyncMock,
    ) -> None:
        """Test successful item update with Q-prefixed ID"""
        request = EntityUpdateRequest(
            id="Q123",
            data={
                "type": "item",
                "labels": {"en": {"language": "en", "value": "Updated Item"}},
            },
            edit_summary="test",
            state=EntityState(is_semi_protected=True),
        )

        # Mock the parent update_entity to return a response
        mock_response = EntityResponse(
            id="Q123",
            rev_id=2,
            data={
                "id": "Q123",
                "type": "item",
                "labels": {"en": {"language": "en", "value": "Updated Item"}},
            },
            state=EntityState(
                sp=False,
                locked=False,
                archived=False,
                dangling=False,
                mep=False,
            ),
        )

        with patch.object(
            handler.__class__.__bases__[0], "update_entity", new_callable=AsyncMock
        ) as mock_parent_update:
            mock_parent_update.return_value = mock_response

            result = await handler.update_entity(
                entity_id="Q123",
                request=request,
                vitess_client=mock_vitess_client,
                s3_client=mock_s3_client,
                stream_producer=mock_stream_producer,
            )

            # Verify parent method was called
            mock_parent_update.assert_called_once_with(
                "Q123",
                request,
                mock_vitess_client,
                mock_s3_client,
                mock_stream_producer,
                None,
            )
            assert result == mock_response

    @pytest.mark.asyncio
    async def test_update_item_invalid_id_property(
        self,
        handler: ItemUpdateHandler,
        mock_vitess_client: MagicMock,
        mock_s3_client: MagicMock,
        mock_stream_producer: AsyncMock,
    ) -> None:
        """Test update fails for property ID (P-prefixed)"""
        request = EntityUpdateRequest(
            id="P123", data={"type": "item"}, edit_summary="test"
        )

        with pytest.raises(ValueError) as exc_info:
            await handler.update_entity(
                entity_id="P123",
                request=request,
                vitess_client=mock_vitess_client,
                s3_client=mock_s3_client,
                stream_producer=mock_stream_producer,
            )

        assert "Entity ID must be an item" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_item_invalid_id_lexeme(
        self,
        handler: ItemUpdateHandler,
        mock_vitess_client: MagicMock,
        mock_s3_client: MagicMock,
        mock_stream_producer: AsyncMock,
    ) -> None:
        """Test update fails for lexeme ID (L-prefixed)"""
        request = EntityUpdateRequest(
            id="L123", data={"type": "item"}, edit_summary="test"
        )

        with pytest.raises(ValueError) as exc_info:
            await handler.update_entity(
                entity_id="L123",
                request=request,
                vitess_client=mock_vitess_client,
                s3_client=mock_s3_client,
                stream_producer=mock_stream_producer,
            )

        assert "Entity ID must be an item" in str(exc_info.value)
