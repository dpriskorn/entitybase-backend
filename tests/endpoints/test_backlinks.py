import pytest
from unittest.mock import Mock, MagicMock
from fastapi import HTTPException
from models.rest_api.handlers.entity.backlinks import BacklinkHandler


class TestBacklinkAPI:
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.handler = BacklinkHandler()
        self.vitess_client = Mock()

    @pytest.mark.asyncio
    async def test_get_backlinks_success(self) -> None:
        """Test successful backlinks retrieval."""
        entity_id = "Q5"
        mock_results = [
            {
                "referencing_internal_id": 123,
                "statement_hash": 456,
                "property_id": "P31",
                "rank": "normal",
            },
            {
                "referencing_internal_id": 124,
                "statement_hash": 457,
                "property_id": "P17",
                "rank": "preferred",
            },
        ]

        # Mock connection and resolvers
        mock_conn = Mock()
        mock_cm = MagicMock()
        mock_cm.__enter__.return_value = mock_conn
        mock_cm.__exit__.return_value = None
        self.vitess_client.connection_manager.get_connection.return_value = mock_cm
        self.vitess_client.id_resolver.resolve_id.return_value = 555  # Q5 -> 555
        self.vitess_client.get_backlinks.return_value = mock_results
        self.vitess_client.id_resolver.resolve_entity_id.side_effect = (
            lambda conn, iid: {123: "Q123", 124: "Q124"}.get(iid, "")
        )

        result = await self.handler.get(entity_id, self.vitess_client)

        expected = {
            "backlinks": [
                {"entity_id": "Q123", "property_id": "P31", "rank": "normal"},
                {"entity_id": "Q124", "property_id": "P17", "rank": "preferred"},
            ],
            "limit": 100,
            "offset": 0,
        }
        assert result.model_dump() == expected

    @pytest.mark.asyncio
    async def test_get_backlinks_entity_not_found(self) -> None:
        """Test 404 when entity doesn't exist."""
        entity_id = "Q999"

        mock_conn = Mock()
        mock_cm = MagicMock()
        mock_cm.__enter__.return_value = mock_conn
        mock_cm.__exit__.return_value = None
        self.vitess_client.connection_manager.get_connection.return_value = mock_cm
        self.vitess_client.id_resolver.resolve_id.return_value = 0  # not found

        with pytest.raises(HTTPException) as exc_info:
            await self.handler.get(entity_id, self.vitess_client)

        assert exc_info.value.status_code == 404
        assert "Entity not found" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_backlinks_empty_results(self) -> None:
        """Test empty backlinks list."""
        entity_id = "Q5"

        mock_conn = Mock()
        mock_cm = MagicMock()
        mock_cm.__enter__.return_value = mock_conn
        mock_cm.__exit__.return_value = None
        self.vitess_client.connection_manager.get_connection.return_value = mock_cm
        self.vitess_client.id_resolver.resolve_id.return_value = 555
        self.vitess_client.get_backlinks.return_value = []

        result = await self.handler.get(entity_id, self.vitess_client)

        expected = {"backlinks": [], "limit": 100, "offset": 0}
        assert result.model_dump() == expected

    @pytest.mark.asyncio
    async def test_get_backlinks_with_pagination(self) -> None:
        """Test backlinks with custom pagination."""
        entity_id = "Q5"
        limit = 50
        offset = 25
        mock_results = [
            {
                "referencing_internal_id": 123,
                "statement_hash": 456,
                "property_id": "P31",
                "rank": "normal",
            }
        ]

        mock_conn = Mock()
        mock_cm = MagicMock()
        mock_cm.__enter__.return_value = mock_conn
        mock_cm.__exit__.return_value = None
        self.vitess_client.connection_manager.get_connection.return_value = mock_cm
        self.vitess_client.id_resolver.resolve_id.return_value = 555
        self.vitess_client.get_backlinks.return_value = mock_results
        self.vitess_client.id_resolver.resolve_entity_id.return_value = "Q123"

        result = await self.handler.get(entity_id, self.vitess_client, limit, offset)

        expected = {
            "backlinks": [
                {"entity_id": "Q123", "property_id": "P31", "rank": "normal"}
            ],
            "limit": 50,
            "offset": 25,
        }
        assert result.model_dump() == expected

    @pytest.mark.asyncio
    async def test_get_backlinks_referencing_entity_not_found(self) -> None:
        """Test handling when referencing entity cannot be resolved."""
        entity_id = "Q5"
        mock_results = [
            {
                "referencing_internal_id": 123,
                "statement_hash": 456,
                "property_id": "P31",
                "rank": "normal",
            },
            {
                "referencing_internal_id": 999,
                "statement_hash": 457,
                "property_id": "P17",
                "rank": "preferred",
            },  # not resolvable
        ]

        mock_conn = Mock()
        mock_cm = MagicMock()
        mock_cm.__enter__.return_value = mock_conn
        mock_cm.__exit__.return_value = None
        self.vitess_client.connection_manager.get_connection.return_value = mock_cm
        self.vitess_client.id_resolver.resolve_id.return_value = 555
        self.vitess_client.get_backlinks.return_value = mock_results
        self.vitess_client.id_resolver.resolve_entity_id.side_effect = (
            lambda conn, iid: {
                123: "Q123",
                999: "",  # not found
            }.get(iid, "")
        )

        result = await self.handler.get(entity_id, self.vitess_client)

        # Should only include resolvable entities
        expected = {
            "backlinks": [
                {"entity_id": "Q123", "property_id": "P31", "rank": "normal"}
            ],
            "limit": 100,
            "offset": 0,
        }
        assert result.model_dump() == expected

    @pytest.mark.asyncio
    async def test_get_backlinks_large_result_set(self) -> None:
        """Test handling of large result sets."""
        entity_id = "Q5"
        # Simulate 150 results (more than default limit)
        mock_results = [
            {
                "referencing_internal_id": i,
                "statement_hash": 456 + i,
                "property_id": "P31",
                "rank": "normal",
            }
            for i in range(150)
        ]

        mock_conn = Mock()
        mock_cm = MagicMock()
        mock_cm.__enter__.return_value = mock_conn
        mock_cm.__exit__.return_value = None
        self.vitess_client.connection_manager.get_connection.return_value = mock_cm
        self.vitess_client.id_resolver.resolve_id.return_value = 555
        self.vitess_client.get_backlinks.return_value = mock_results[
            :100
        ]  # Repository limits to 100
        self.vitess_client.id_resolver.resolve_entity_id.side_effect = (
            lambda conn, iid: f"Q{iid}"
        )

        result = await self.handler.get(entity_id, self.vitess_client)

        assert len(result.backlinks) == 100
        assert result.limit == 100
        assert result.offset == 0

    @pytest.mark.asyncio
    async def test_connection_context_management(self) -> None:
        """Test that database connections are properly managed."""
        entity_id = "Q5"

        mock_conn = Mock()
        mock_cm = MagicMock()
        mock_cm.__enter__.return_value = mock_conn
        mock_cm.__exit__.return_value = None
        self.vitess_client.connection_manager.get_connection.return_value = mock_cm
        self.vitess_client.id_resolver.resolve_id.return_value = 555
        self.vitess_client.get_backlinks.return_value = []

        await self.handler.get(entity_id, self.vitess_client)

        # Verify context manager usage
        self.vitess_client.connection_manager.get_connection.assert_called_once()
        self.vitess_client.connection_manager.get_connection.return_value.__enter__.assert_called_once()
        self.vitess_client.connection_manager.get_connection.return_value.__exit__.assert_called_once()
