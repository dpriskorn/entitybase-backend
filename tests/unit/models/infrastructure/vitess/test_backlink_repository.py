import pytest
from unittest.mock import MagicMock, patch

pytestmark = pytest.mark.unit

from models.infrastructure.vitess.repositories.backlink import BacklinkRepository


class TestBacklinkRepository:
    def test_init(self) -> None:
        """Test BacklinkRepository initialization."""
        mock_connection_manager = MagicMock()

        repo = BacklinkRepository(mock_connection_manager)

        assert repo.connection_manager == mock_connection_manager

    def test_insert_backlinks_success(self) -> None:
        """Test successful backlinks insertion."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = BacklinkRepository(mock_connection_manager)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        backlinks = [(1, 2, 123, "P31", "normal")]
        result = repo.insert_backlinks(mock_conn, backlinks)

        assert result.success is True
        mock_cursor.executemany.assert_called_once()

    def test_insert_backlinks_empty(self) -> None:
        """Test inserting empty backlinks list."""
        mock_connection_manager = MagicMock()

        repo = BacklinkRepository(mock_connection_manager)

        result = repo.insert_backlinks(None, [])

        assert result.success is True

    def test_insert_backlinks_failure(self) -> None:
        """Test backlinks insertion failure."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = BacklinkRepository(mock_connection_manager)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.executemany.side_effect = Exception("DB error")

        backlinks = [(1, 2, 123, "P31", "normal")]
        result = repo.insert_backlinks(mock_conn, backlinks)

        assert result.success is False
        assert "DB error" in result.error

    def test_delete_backlinks_for_entity_success(self) -> None:
        """Test successful backlinks deletion."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = BacklinkRepository(mock_connection_manager)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        result = repo.delete_backlinks_for_entity(mock_conn, 123)

        assert result.success is True
        mock_cursor.execute.assert_called_once()

    def test_delete_backlinks_for_entity_invalid_id(self) -> None:
        """Test deletion with invalid ID."""
        mock_connection_manager = MagicMock()

        repo = BacklinkRepository(mock_connection_manager)

        result = repo.delete_backlinks_for_entity(None, 0)

        assert result.success is False
        assert "Invalid referencing internal ID" in result.error

    def test_delete_backlinks_for_entity_failure(self) -> None:
        """Test backlinks deletion failure."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = BacklinkRepository(mock_connection_manager)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB error")

        result = repo.delete_backlinks_for_entity(mock_conn, 123)

        assert result.success is False
        assert "DB error" in result.error

    def test_get_backlinks(self) -> None:
        """Test getting backlinks."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = BacklinkRepository(mock_connection_manager)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            (456, 789, "P31", "normal"),
            (789, 101, "P279", "preferred")
        ]

        result = repo.get_backlinks(mock_conn, 123, 50, 10)

        assert len(result) == 2
        assert result[0].referencing_internal_id == 456
        assert result[0].statement_hash == "789"
        assert result[0].property_id == "P31"
        assert result[0].rank == "normal"
        mock_cursor.execute.assert_called_once()

    @patch("models.infrastructure.vitess.repositories.backlink.raise_validation_error")
    def test_insert_backlink_statistics_invalid_date(self, mock_raise) -> None:
        """Test inserting statistics with invalid date."""
        mock_connection_manager = MagicMock()

        repo = BacklinkRepository(mock_connection_manager)

        repo.insert_backlink_statistics(None, "invalid", 100, 50, [])

        mock_raise.assert_called_once()
        call_args = mock_raise.call_args[0]
        assert "Invalid date format" in call_args[0]

    @patch("models.infrastructure.vitess.repositories.backlink.raise_validation_error")
    def test_insert_backlink_statistics_negative_total(self, mock_raise) -> None:
        """Test inserting statistics with negative total."""
        mock_connection_manager = MagicMock()

        repo = BacklinkRepository(mock_connection_manager)

        repo.insert_backlink_statistics(None, "2023-01-01", -1, 50, [])

        mock_raise.assert_called_once()
        call_args = mock_raise.call_args[0]
        assert "total_backlinks must be non-negative" in call_args[0]

    @patch("models.infrastructure.vitess.repositories.backlink.raise_validation_error")
    def test_insert_backlink_statistics_invalid_top_entities(self, mock_raise) -> None:
        """Test inserting statistics with invalid top entities."""
        mock_connection_manager = MagicMock()

        repo = BacklinkRepository(mock_connection_manager)

        repo.insert_backlink_statistics(None, "2023-01-01", 100, 50, "not_list")

        mock_raise.assert_called_once()
        call_args = mock_raise.call_args[0]
        assert "top_entities_by_backlinks must be a list" in call_args[0]

    def test_insert_backlink_statistics_success(self) -> None:
        """Test successful statistics insertion."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = BacklinkRepository(mock_connection_manager)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        top_entities = [{"id": "Q1", "count": 10}]
        repo.insert_backlink_statistics(mock_conn, "2023-01-01", 100, 50, top_entities)

        mock_cursor.execute.assert_called_once()
        call_args = mock_cursor.execute.call_args[0]
        assert "INSERT INTO backlink_statistics" in call_args[0]
        assert "2023-01-01" in call_args[1]
        assert 100 in call_args[1]
        assert 50 in call_args[1]

    @patch("models.infrastructure.vitess.repositories.backlink.json.dumps")
    @patch("models.infrastructure.vitess.repositories.backlink.raise_validation_error")
    def test_insert_backlink_statistics_json_error(self, mock_raise, mock_json) -> None:
        """Test statistics insertion with JSON serialization error."""
        mock_connection_manager = MagicMock()
        mock_json.side_effect = TypeError("JSON error")

        repo = BacklinkRepository(mock_connection_manager)

        repo.insert_backlink_statistics(None, "2023-01-01", 100, 50, [object()])

        mock_raise.assert_called_once()
        call_args = mock_raise.call_args[0]
        assert "Failed to serialize" in call_args[0]

    def test_insert_backlink_statistics_db_error(self) -> None:
        """Test statistics insertion database error."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = BacklinkRepository(mock_connection_manager)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB insert error")

        with pytest.raises(Exception, match="DB insert error"):
            repo.insert_backlink_statistics(mock_conn, "2023-01-01", 100, 50, [])