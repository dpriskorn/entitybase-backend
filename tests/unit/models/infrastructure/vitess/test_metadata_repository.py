import pytest
from unittest.mock import MagicMock

pytestmark = pytest.mark.unit

from models.infrastructure.vitess.repositories.metadata import MetadataRepository


class TestMetadataRepository:
    def test_init(self) -> None:
        """Test MetadataRepository initialization."""
        mock_connection_manager = MagicMock()

        repo = MetadataRepository(mock_connection_manager)

        assert repo.connection_manager == mock_connection_manager

    def test_insert_metadata_content_success(self) -> None:
        """Test successful metadata content insertion."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = MetadataRepository(mock_connection_manager)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        result = repo.insert_metadata_content(mock_conn, 12345, "property")

        assert result.success is True
        mock_cursor.execute.assert_called_once()

    def test_insert_metadata_content_db_error(self) -> None:
        """Test metadata content insertion database error."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = MetadataRepository(mock_connection_manager)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB error")

        result = repo.insert_metadata_content(mock_conn, 12345, "property")

        assert result.success is False
        assert "DB error" in result.error

    def test_get_metadata_content_success(self) -> None:
        """Test successful metadata content retrieval."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = MetadataRepository(mock_connection_manager)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (5,)

        result = repo.get_metadata_content(mock_conn, 12345, "property")

        assert result.success is True
        assert result.data.ref_count == 5

    def test_get_metadata_content_invalid_params(self) -> None:
        """Test metadata content retrieval with invalid parameters."""
        mock_connection_manager = MagicMock()

        repo = MetadataRepository(mock_connection_manager)

        result = repo.get_metadata_content(None, 0, "property")

        assert result.success is False
        assert "Invalid content hash or type" in result.error

    def test_get_metadata_content_not_found(self) -> None:
        """Test metadata content retrieval when not found."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = MetadataRepository(mock_connection_manager)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        result = repo.get_metadata_content(mock_conn, 12345, "property")

        assert result.success is False
        assert "Metadata content not found" in result.error

    def test_get_metadata_content_db_error(self) -> None:
        """Test metadata content retrieval database error."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = MetadataRepository(mock_connection_manager)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB error")

        result = repo.get_metadata_content(mock_conn, 12345, "property")

        assert result.success is False
        assert "DB error" in result.error

    def test_decrement_ref_count_success(self) -> None:
        """Test successful ref count decrement."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = MetadataRepository(mock_connection_manager)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (0,)  # ref_count now 0

        result = repo.decrement_ref_count(mock_conn, 12345, "property")

        assert result.success is True
        assert result.data is True  # ref_count <= 0

    def test_decrement_ref_count_invalid_params(self) -> None:
        """Test decrement ref count with invalid parameters."""
        mock_connection_manager = MagicMock()

        repo = MetadataRepository(mock_connection_manager)

        result = repo.decrement_ref_count(None, -1, "")

        assert result.success is False
        assert "Invalid content hash or type" in result.error

    def test_decrement_ref_count_not_found(self) -> None:
        """Test decrement ref count when not found."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = MetadataRepository(mock_connection_manager)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        result = repo.decrement_ref_count(mock_conn, 12345, "property")

        assert result.success is False
        assert "Metadata content not found" in result.error

    def test_decrement_ref_count_db_error(self) -> None:
        """Test decrement ref count database error."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = MetadataRepository(mock_connection_manager)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB error")

        result = repo.decrement_ref_count(mock_conn, 12345, "property")

        assert result.success is False
        assert "DB error" in result.error

    def test_delete_metadata_content(self) -> None:
        """Test deleting metadata content."""
        mock_connection_manager = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = MetadataRepository(mock_connection_manager)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        repo.delete_metadata_content(mock_conn, 12345, "property")

        mock_cursor.execute.assert_called_once()