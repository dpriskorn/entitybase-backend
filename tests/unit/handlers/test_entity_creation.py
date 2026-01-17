import sys
from unittest.mock import AsyncMock, MagicMock

import pytest

pytestmark = pytest.mark.unit

sys.path.insert(0, "src")

from models.rest_api.entitybase.request.entity import EntityCreateRequest
from models.rest_api.entitybase.handlers.entity.item import ItemCreateHandler
from models.rest_api.entitybase.handlers.entity.property.create import (
    PropertyCreateHandler,
)
from models.rest_api.entitybase.services.enumeration_service import EnumerationService


class TestItemCreateHandler:
    """Unit tests for ItemCreateHandler"""

    @pytest.fixture
    def enumeration_service(self) -> EnumerationService:
        """Mock enumeration service"""
        service = MagicMock(spec=EnumerationService)
        service.get_next_entity_id.return_value = "Q123"
        return service

    @pytest.fixture
    def handler(self, enumeration_service: EnumerationService) -> ItemCreateHandler:
        """Create handler instance"""
        return ItemCreateHandler(enumeration_service)

    @pytest.fixture
    def mock_vitess_client(self) -> MagicMock:
        """Mock vitess client"""
        client = MagicMock()
        client.entity_exists.return_value = False
        client.register_entity = MagicMock()
        client.is_entity_deleted.return_value = False
        client.get_head.return_value = 0
        client.create_revision = MagicMock()
        client.write_entity_revision = MagicMock()
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
    async def test_create_item_success(
        self,
        handler: ItemCreateHandler,
        mock_vitess_client: MagicMock,
        mock_s3_client: MagicMock,
        mock_stream_producer: AsyncMock,
    ) -> None:
        """Test successful item creation"""
        request = EntityCreateRequest(
            id="Q999",
            labels={"en": {"language": "en", "value": "Test Item"}},
            edit_summary="Test creation",
        )

        mock_vitess_client.entity_exists.return_value = False

        result = await handler.create_entity(
            request=request,
            vitess_client=mock_vitess_client,
            s3_client=mock_s3_client,
            stream_producer=mock_stream_producer,
        )

        # Verify enumeration service was called
        handler.enumeration_service.get_next_entity_id.assert_called_once_with("item")

        # Verify vitess interactions
        mock_vitess_client.entity_exists.assert_called_once_with("Q123")
        mock_vitess_client.register_entity.assert_called_once_with("Q123")
        mock_vitess_client.is_entity_deleted.assert_called_once_with("Q123")

        # Verify response
        assert result.id == "Q123"
        assert result.revision_id == 1
        assert "id" in result.data
        assert result.data["id"] == "Q123"

    @pytest.mark.asyncio
    async def test_create_item_entity_exists(
        self,
        handler: ItemCreateHandler,
        mock_vitess_client: MagicMock,
        mock_s3_client: MagicMock,
        mock_stream_producer: AsyncMock,
    ) -> None:
        """Test item creation fails if entity already exists"""
        mock_vitess_client.entity_exists.return_value = True

        request = EntityCreateRequest(id="Q123", edit_summary="test")

        with pytest.raises(Exception) as exc_info:
            await handler.create_entity(
                request=request,
                vitess_client=mock_vitess_client,
                s3_client=mock_s3_client,
                stream_producer=mock_stream_producer,
            )

        assert "already exists" in str(exc_info.value)


class TestPropertyCreateHandler:
    """Unit tests for PropertyCreateHandler"""

    @pytest.fixture
    def enumeration_service(self) -> EnumerationService:
        """Mock enumeration service"""
        service = MagicMock(spec=EnumerationService)
        service.get_next_entity_id.return_value = "P456"
        return service

    @pytest.fixture
    def handler(self, enumeration_service: EnumerationService) -> PropertyCreateHandler:
        """Create handler instance"""
        return PropertyCreateHandler(enumeration_service)

    @pytest.fixture
    def mock_vitess_client(self) -> MagicMock:
        """Mock vitess client"""
        client = MagicMock()
        client.entity_exists.return_value = False
        client.register_entity = MagicMock()
        client.is_entity_deleted.return_value = False
        client.get_head.return_value = 0
        client.create_revision = MagicMock()
        client.write_entity_revision = MagicMock()
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
    async def test_create_property_success(
        self,
        handler: PropertyCreateHandler,
        mock_vitess_client: MagicMock,
        mock_s3_client: MagicMock,
        mock_stream_producer: AsyncMock,
    ) -> None:
        """Test successful property creation"""
        request = EntityCreateRequest(
            labels={"en": {"language": "en", "value": "Test Property"}},
            edit_summary="Test property creation",
            editor="test",
        )

        mock_vitess_client.entity_exists.return_value = False

        result = await handler.create_entity(
            request=request,
            vitess_client=mock_vitess_client,
            s3_client=mock_s3_client,
            stream_producer=mock_stream_producer,
        )

        # Verify enumeration service was called
        handler.enumeration_service.get_next_entity_id.assert_called_once_with(
            "property"
        )

        # Verify vitess interactions
        mock_vitess_client.entity_exists.assert_called_once_with("P456")
        mock_vitess_client.register_entity.assert_called_once_with("P456")
        mock_vitess_client.is_entity_deleted.assert_called_once_with("P456")

        # Verify response
        assert result.id == "P456"
        assert result.revision_id == 1
        assert "id" in result.data
        assert result.data["id"] == "P456"
