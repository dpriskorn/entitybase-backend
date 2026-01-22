"""Unit tests for BacklinkRepository."""

import pytest
from unittest.mock import MagicMock, mock_open

from models.infrastructure.vitess.repositories.backlink import BacklinkRepository
from models.data.infrastructure.vitess.records.backlink_entry import BacklinkRecord


class TestBacklinkRepository:
    """Unit tests for BacklinkRepository."""

    def test_insert_backlinks_success(self):
        """Test successful backlink insertion."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=None)
        mock_vitess_client.cursor = mock_cursor

        repo = BacklinkRepository(vitess_client=mock_vitess_client)

        backlinks = [(1, 2, 123, "P31", "normal")]
        result = repo.insert_backlinks(backlinks)

        assert result.success is True
        mock_cursor.executemany.assert_called_once()

    def test_insert_backlinks_empty(self):
        """Test inserting empty backlinks list."""
        mock_vitess_client = MagicMock()

        repo = BacklinkRepository(vitess_client=mock_vitess_client)

        result = repo.insert_backlinks([])

        assert result.success is True

    def test_insert_backlinks_error(self):
        """Test backlink insertion with database error."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=None)
        mock_cursor.executemany.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = BacklinkRepository(vitess_client=mock_vitess_client)

        backlinks = [(1, 2, 123, "P31", "normal")]
        result = repo.insert_backlinks(backlinks)

        assert result.success is False
        assert "DB error" in result.error

    def test_delete_backlinks_for_entity_success(self):
        """Test successful backlink deletion."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_vitess_client.cursor = mock_cursor

        repo = BacklinkRepository(vitess_client=mock_vitess_client)

        result = repo.delete_backlinks_for_entity(123)

        assert result.success is True
        mock_cursor.execute.assert_called_once_with(
            "DELETE FROM entity_backlinks WHERE referencing_internal_id = %s", (123,)
        )

    def test_delete_backlinks_for_entity_invalid_id(self):
        """Test deletion with invalid ID."""
        mock_vitess_client = MagicMock()

        repo = BacklinkRepository(vitess_client=mock_vitess_client)

        result = repo.delete_backlinks_for_entity(0)

        assert result.success is False
        assert "Invalid referencing internal ID" in result.error

    def test_get_backlinks_success(self):
        """Test getting backlinks."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [(2, 123, "P31", "normal")]
        mock_vitess_client.cursor = mock_cursor

        repo = BacklinkRepository(vitess_client=mock_vitess_client)

        result = repo.get_backlinks(1)

        assert len(result) == 1
        assert isinstance(result[0], BacklinkRecord)
        assert result[0].referencing_internal_id == 2

    def test_get_backlinks_empty(self):
        """Test getting backlinks when none exist."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_vitess_client.cursor = mock_cursor

        repo = BacklinkRepository(vitess_client=mock_vitess_client)

        result = repo.get_backlinks(1)

        assert result == []

    def test_insert_backlink_statistics_success(self):
        """Test successful statistics insertion."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_vitess_client.cursor = mock_cursor

        repo = BacklinkRepository(vitess_client=mock_vitess_client)

        repo.insert_backlink_statistics("2023-01-01", 100, 50, [{"id": "Q1", "count": 10}])

        mock_cursor.execute.assert_called_once()

    def test_insert_backlink_statistics_invalid_date(self):
        """Test statistics insertion with invalid date."""
        mock_vitess_client = MagicMock()

        repo = BacklinkRepository(vitess_client=mock_vitess_client)

        with pytest.raises(Exception):  # raise_validation_error
            repo.insert_backlink_statistics("invalid", 100, 50, [])

    def test_insert_backlink_statistics_negative_values(self):
        """Test statistics insertion with negative values."""
        mock_vitess_client = MagicMock()

        repo = BacklinkRepository(vitess_client=mock_vitess_client)

        with pytest.raises(Exception):
            repo.insert_backlink_statistics("2023-01-01", -1, 50, [])
