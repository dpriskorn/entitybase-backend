import pytest
from unittest.mock import MagicMock

pytestmark = pytest.mark.unit

from models.infrastructure.vitess.repositories.listing import ListingRepository


class TestListingRepository:
    def test_init(self) -> None:
        """Test ListingRepository initialization."""
        mock_connection_manager = MagicMock()

        repo = ListingRepository(mock_connection_manager)

        assert repo.connection_manager == mock_connection_manager

    def test_list_locked(self) -> None:
        """Test listing locked entities."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = ListingRepository(mock_connection_manager)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ("Q42", "item"),
            ("Q43", "property")
        ]

        result = repo.list_locked(mock_conn, 10)

        assert len(result) == 2
        assert result[0].entity_id == "Q42"
        assert result[0].entity_type == "item"
        assert result[0].reason == "locked"
        assert result[1].entity_id == "Q43"
        assert result[1].entity_type == "property"
        assert result[1].reason == "locked"

    def test_list_semi_protected(self) -> None:
        """Test listing semi-protected entities."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = ListingRepository(mock_connection_manager)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ("Q42", "item")
        ]

        result = repo.list_semi_protected(mock_conn, 10)

        assert len(result) == 1
        assert result[0].entity_id == "Q42"
        assert result[0].entity_type == "item"
        assert result[0].reason == "semi_protected"

    def test_list_archived(self) -> None:
        """Test listing archived entities."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = ListingRepository(mock_connection_manager)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ("Q42", "item")
        ]

        result = repo.list_archived(mock_conn, 10)

        assert len(result) == 1
        assert result[0].entity_id == "Q42"
        assert result[0].entity_type == "item"
        assert result[0].reason == "archived"

    def test_list_dangling(self) -> None:
        """Test listing dangling entities."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = ListingRepository(mock_connection_manager)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ("Q42", "item")
        ]

        result = repo.list_dangling(mock_conn, 10)

        assert len(result) == 1
        assert result[0].entity_id == "Q42"
        assert result[0].entity_type == "item"
        assert result[0].reason == "dangling"

    def test_list_entities_by_edit_type(self) -> None:
        """Test listing entities by edit type."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = ListingRepository(mock_connection_manager)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            ("Q42", "item", "create")
        ]

        result = repo._list_entities_by_edit_type(mock_conn, "create", 10)

        assert len(result) == 1
        assert result[0].entity_id == "Q42"
        assert result[0].entity_type == "item"
        assert result[0].reason == "create"