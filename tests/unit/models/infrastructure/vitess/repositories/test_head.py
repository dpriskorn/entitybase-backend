"""Unit tests for HeadRepository."""

from unittest.mock import MagicMock

from models.infrastructure.vitess.repositories.head import HeadRepository


class TestHeadRepository:
    """Unit tests for HeadRepository."""

    def test_get_head_revision_success(self):
        """Test getting head revision successfully."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchone.return_value = (15,)
        mock_vitess_client.cursor = mock_cursor

        repo = HeadRepository(vitess_client=mock_vitess_client)

        result = repo.get_head_revision(123)

        assert result.success is True
        assert result.data == 15

    def test_get_head_revision_entity_not_found(self):
        """Test getting head revision when entity not found."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchone.return_value = None
        mock_vitess_client.cursor = mock_cursor

        repo = HeadRepository(vitess_client=mock_vitess_client)

        result = repo.get_head_revision(123)

        assert result.success is False
        assert "Entity not found" in result.error

    def test_get_head_revision_invalid_id(self):
        """Test getting head revision with invalid ID."""
        mock_vitess_client = MagicMock()

        repo = HeadRepository(vitess_client=mock_vitess_client)

        result = repo.get_head_revision(0)

        assert result.success is False
        assert "Invalid internal entity ID" in result.error

    def test_get_head_revision_database_error(self):
        """Test getting head revision with database error."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.execute.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = HeadRepository(vitess_client=mock_vitess_client)

        result = repo.get_head_revision(123)

        assert result.success is False
        assert "DB error" in result.error
