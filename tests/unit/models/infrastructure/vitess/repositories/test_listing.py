"""Unit tests for ListingRepository."""

from unittest.mock import MagicMock

from models.infrastructure.vitess.repositories.listing import ListingRepository
from models.data.rest_api.v1.entitybase.response import EntityListing


class TestListingRepository:
    """Unit tests for ListingRepository."""

    def test_list_locked_success(self):
        """Test listing locked entities."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchall.return_value = [("Q1", "item"), ("Q2", "property")]
        mock_vitess_client.cursor = mock_cursor

        repo = ListingRepository(vitess_client=mock_vitess_client)

        result = repo.list_locked(10)

        assert len(result) == 2
        assert isinstance(result[0], EntityListing)
        assert result[0].entity_id == "Q1"
        assert result[0].reason == "locked"

    def test_list_locked_empty(self):
        """Test listing locked entities when none exist."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchall.return_value = []
        mock_vitess_client.cursor = mock_cursor

        repo = ListingRepository(vitess_client=mock_vitess_client)

        result = repo.list_locked(10)

        assert result == []

    def test_list_semi_protected_success(self):
        """Test listing semi-protected entities."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchall.return_value = [("Q3", "item")]
        mock_vitess_client.cursor = mock_cursor

        repo = ListingRepository(vitess_client=mock_vitess_client)

        result = repo.list_semi_protected(10)

        assert len(result) == 1
        assert result[0].reason == "semi_protected"

    def test_list_archived_success(self):
        """Test listing archived entities."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchall.return_value = [("Q4", "property")]
        mock_vitess_client.cursor = mock_cursor

        repo = ListingRepository(vitess_client=mock_vitess_client)

        result = repo.list_archived(10)

        assert len(result) == 1
        assert result[0].reason == "archived"

    def test_list_dangling_success(self):
        """Test listing dangling entities."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchall.return_value = [("Q5", "item")]
        mock_vitess_client.cursor = mock_cursor

        repo = ListingRepository(vitess_client=mock_vitess_client)

        result = repo.list_dangling(10)

        assert len(result) == 1
        assert result[0].reason == "dangling"

    def test_list_semi_protected_empty(self):
        """Test listing semi-protected entities when none exist."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchall.return_value = []
        mock_vitess_client.cursor = mock_cursor

        repo = ListingRepository(vitess_client=mock_vitess_client)

        result = repo.list_semi_protected(10)

        assert result == []

    def test_list_archived_empty(self):
        """Test listing archived entities when none exist."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchall.return_value = []
        mock_vitess_client.cursor = mock_cursor

        repo = ListingRepository(vitess_client=mock_vitess_client)

        result = repo.list_archived(10)

        assert result == []

    def test_list_dangling_empty(self):
        """Test listing dangling entities when none exist."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchall.return_value = []
        mock_vitess_client.cursor = mock_cursor

        repo = ListingRepository(vitess_client=mock_vitess_client)

        result = repo.list_dangling(10)

        assert result == []

    def test_list_entities_by_edit_type_empty(self):
        """Test listing entities by edit type when none exist."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchall.return_value = []
        mock_vitess_client.cursor = mock_cursor

        repo = ListingRepository(vitess_client=mock_vitess_client)

        result = repo._list_entities_by_edit_type("mass_edit", 10)

        assert result == []
