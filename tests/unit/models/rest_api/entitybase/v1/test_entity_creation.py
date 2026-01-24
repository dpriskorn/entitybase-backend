import sys
from unittest.mock import AsyncMock, MagicMock

import pytest

pytestmark = pytest.mark.unit

sys.path.insert(0, "src")

from models.data.rest_api.v1.entitybase.request import EntityCreateRequest
from models.rest_api.entitybase.v1.handlers.entity.item import ItemCreateHandler
from models.rest_api.entitybase.v1.handlers.entity.property.create import (
    PropertyCreateHandler,
)
from models.rest_api.entitybase.v1.services.enumeration_service import (
    EnumerationService,
)


class TestItemCreateHandler:
    """Unit tests for ItemCreateHandler"""

    @pytest.fixture
    def enumeration_service(self) -> EnumerationService:
        """Mock enumeration service"""
        service = MagicMock(spec=EnumerationService)
        service.get_next_entity_id.return_value = "Q123"
        return service

    @pytest.fixture
    def handler(
        self, enumeration_service: EnumerationService, mock_vitess_client: MagicMock
    ) -> ItemCreateHandler:
        """Create handler instance"""
        state = MagicMock()
        state.vitess_client = mock_vitess_client
        state.vitess_config = None
        state.s3_client = MagicMock()
        state.entity_change_stream_producer = AsyncMock()
        return ItemCreateHandler(enumeration_service=enumeration_service, state=state)

    @pytest.fixture
    def mock_vitess_client(self) -> MagicMock:
        """Mock vitess client"""
        client = MagicMock()
        client.entity_exists.return_value = False
        client.id_resolver.entity_exists.return_value = False
        client.entity_repository.create_entity = MagicMock()
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
            id="Q99999",
            labels={"en": {"language": "en", "value": "Test Item"}},
            edit_summary="Test creation",
        )

        mock_vitess_client.entity_exists.return_value = False
        mock_vitess_client.get_protection_info.return_value = MagicMock(
            is_archived=False, is_locked=False, is_mass_edit_protected=False
        )
        mock_vitess_client.entity_repository.get_entity.return_value = MagicMock(
            is_deleted=False, is_archived=False
        )

        result = await handler.create_entity(request=request)

        # Verify vitess interactions
        mock_vitess_client.id_resolver.entity_exists.assert_called_once_with("Q99999")
        mock_vitess_client.entity_repository.create_entity.assert_called_once_with(
            "Q99999"
        )

        # Verify response
        assert result.id == "Q99999"
        assert result.revision_id == 1
        assert "id" in result.entity_data
        assert result.entity_data["id"] == "Q99999"

    @pytest.mark.asyncio
    async def test_create_item_entity_exists(
        self,
        handler: ItemCreateHandler,
        mock_vitess_client: MagicMock,
        mock_s3_client: MagicMock,
        mock_stream_producer: AsyncMock,
    ) -> None:
        """Test item creation fails if entity already exists"""
        mock_vitess_client.id_resolver.entity_exists.return_value = True

        request = EntityCreateRequest(id="Q123", edit_summary="test")

        with pytest.raises(Exception) as exc_info:
            await handler.create_entity(request=request)

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
    def handler(
        self,
        enumeration_service: EnumerationService,
        mock_vitess_client: MagicMock,
        mock_s3_client: MagicMock,
        mock_stream_producer: MagicMock,
    ) -> PropertyCreateHandler:
        """Create handler instance"""
        state = MagicMock()
        state.vitess_client = mock_vitess_client
        state.vitess_config = None
        state.s3_client = mock_s3_client
        state.entity_change_stream_producer = mock_stream_producer
        return PropertyCreateHandler(
            enumeration_service=enumeration_service, state=state
        )

    @pytest.fixture
    def mock_vitess_client(self) -> MagicMock:
        """Mock vitess client"""
        client = MagicMock()
        client.entity_exists.return_value = False
        client.id_resolver.entity_exists.return_value = False
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
