import pytest
from unittest.mock import MagicMock

pytestmark = pytest.mark.unit

from models.infrastructure.vitess.repositories.statement import StatementRepository


class TestStatementRepository:
    def test_init(self) -> None:
        """Test StatementRepository initialization."""
        mock_connection_manager = MagicMock()

        repo = StatementRepository(mock_connection_manager)

        assert repo.connection_manager == mock_connection_manager

    def test_insert_content_success(self) -> None:
        """Test successful content insertion."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = StatementRepository(mock_connection_manager)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None  # Not exists

        result = repo.insert_content(mock_conn, 12345)

        assert result.success is True
        assert mock_cursor.execute.call_count == 2  # SELECT then INSERT

    def test_insert_content_already_exists(self) -> None:
        """Test inserting content that already exists."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = StatementRepository(mock_connection_manager)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1,)  # Exists

        result = repo.insert_content(mock_conn, 12345)

        assert result.success is False
        assert "already exists" in result.error

    def test_insert_content_db_error(self) -> None:
        """Test content insertion database error."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = StatementRepository(mock_connection_manager)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB error")

        result = repo.insert_content(mock_conn, 12345)

        assert result.success is False
        assert "DB error" in result.error

    def test_increment_ref_count_success(self) -> None:
        """Test successful ref count increment."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = StatementRepository(mock_connection_manager)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (5,)  # New count

        result = repo.increment_ref_count(mock_conn, 12345)

        assert result.success is True
        assert result.data == 5
        assert mock_cursor.execute.call_count == 2  # UPDATE then SELECT

    def test_increment_ref_count_invalid_hash(self) -> None:
        """Test increment with invalid content hash."""
        mock_connection_manager = MagicMock()

        repo = StatementRepository(mock_connection_manager)

        result = repo.increment_ref_count(None, 0)

        assert result.success is False
        assert "Invalid content hash" in result.error

    def test_increment_ref_count_db_error(self) -> None:
        """Test ref count increment database error."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = StatementRepository(mock_connection_manager)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB error")

        result = repo.increment_ref_count(mock_conn, 12345)

        assert result.success is False
        assert "DB error" in result.error

    def test_decrement_ref_count_success(self) -> None:
        """Test successful ref count decrement."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = StatementRepository(mock_connection_manager)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (3,)  # New count

        result = repo.decrement_ref_count(mock_conn, 12345)

        assert result.success is True
        assert result.data == 3

    def test_decrement_ref_count_invalid_hash(self) -> None:
        """Test decrement with invalid content hash."""
        mock_connection_manager = MagicMock()

        repo = StatementRepository(mock_connection_manager)

        result = repo.decrement_ref_count(None, -1)

        assert result.success is False
        assert "Invalid content hash" in result.error

    def test_decrement_ref_count_db_error(self) -> None:
        """Test ref count decrement database error."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = StatementRepository(mock_connection_manager)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB error")

        result = repo.decrement_ref_count(mock_conn, 12345)

        assert result.success is False
        assert "DB error" in result.error

    def test_get_orphaned_success(self) -> None:
        """Test getting orphaned content."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = StatementRepository(mock_connection_manager)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(12345,), (67890,)]

        result = repo.get_orphaned(mock_conn, 30, 100)

        assert result.success is True
        assert result.data == [12345, 67890]

    def test_get_orphaned_invalid_params(self) -> None:
        """Test getting orphaned with invalid parameters."""
        mock_connection_manager = MagicMock()

        repo = StatementRepository(mock_connection_manager)

        result = repo.get_orphaned(None, 0, 100)

        assert result.success is False
        assert "Invalid parameters" in result.error

    def test_get_orphaned_db_error(self) -> None:
        """Test getting orphaned database error."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = StatementRepository(mock_connection_manager)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB error")

        result = repo.get_orphaned(mock_conn, 30, 100)

        assert result.success is False
        assert "DB error" in result.error

    def test_get_most_used(self) -> None:
        """Test getting most used content."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = StatementRepository(mock_connection_manager)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(12345,), (67890,)]

        result = repo.get_most_used(mock_conn, 10, 5)

        assert result == [12345, 67890]

    def test_get_ref_count(self) -> None:
        """Test getting reference count."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = StatementRepository(mock_connection_manager)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (10,)

        result = repo.get_ref_count(mock_conn, 12345)

        assert result == 10

    def test_get_ref_count_not_found(self) -> None:
        """Test getting reference count for non-existent content."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = StatementRepository(mock_connection_manager)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        result = repo.get_ref_count(mock_conn, 12345)

        assert result == 0

    def test_delete_content(self) -> None:
        """Test deleting content."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = StatementRepository(mock_connection_manager)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        repo.delete_content(mock_conn, 12345)

        mock_cursor.execute.assert_called_once()

    def test_get_all_statement_hashes(self) -> None:
        """Test getting all statement hashes."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = StatementRepository(mock_connection_manager)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(12345,), (67890,)]

        result = repo.get_all_statement_hashes(mock_conn)

        assert result == [12345, 67890]</content>
<parameter name="filePath">/home/dpriskorn/src/python/wikibase-backend/tests/unit/models/infrastructure/vitess/test_statement_repository.py