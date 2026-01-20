import pytest
from unittest.mock import MagicMock

pytestmark = pytest.mark.unit

from models.infrastructure.vitess.repositories.head import HeadRepository


class TestHeadRepository:
    def test_init(self) -> None:
        """Test HeadRepository initialization."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()

        repo = HeadRepository(mock_connection_manager, mock_id_resolver)

        assert repo.connection_manager == mock_connection_manager
        assert repo.id_resolver == mock_id_resolver

    def test_cas_update_with_status_success(self) -> None:
        """Test successful CAS update."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = HeadRepository(mock_connection_manager, mock_id_resolver)
        mock_id_resolver.resolve_id.return_value = 123
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 1

        result = repo.cas_update_with_status(mock_conn, "Q42", 100, 200, True, False, False, False, False, False, False)

        assert result.success is True
        mock_cursor.execute.assert_called_once()

    def test_cas_update_with_status_entity_not_found(self) -> None:
        """Test CAS update when entity not found."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()

        repo = HeadRepository(mock_connection_manager, mock_id_resolver)
        mock_id_resolver.resolve_id.return_value = 0

        result = repo.cas_update_with_status(mock_conn=None, entity_id="Q42")

        assert result.success is False
        assert "Entity not found" in result.error

    def test_cas_update_with_status_cas_failed(self) -> None:
        """Test CAS update when CAS fails."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = HeadRepository(mock_connection_manager, mock_id_resolver)
        mock_id_resolver.resolve_id.return_value = 123
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.rowcount = 0

        result = repo.cas_update_with_status(mock_conn, "Q42", 100, 200)

        assert result.success is False
        assert "CAS failed" in result.error

    def test_cas_update_with_status_db_error(self) -> None:
        """Test CAS update database error."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = HeadRepository(mock_connection_manager, mock_id_resolver)
        mock_id_resolver.resolve_id.return_value = 123
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB error")

        result = repo.cas_update_with_status(mock_conn, "Q42", 100, 200)

        assert result.success is False
        assert "DB error" in result.error

    def test_hard_delete_success(self) -> None:
        """Test successful hard delete."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = HeadRepository(mock_connection_manager, mock_id_resolver)
        mock_id_resolver.resolve_id.return_value = 123
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        result = repo.hard_delete(mock_conn, "Q42", 456)

        assert result.success is True
        mock_cursor.execute.assert_called_once()

    def test_hard_delete_entity_not_found(self) -> None:
        """Test hard delete when entity not found."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()

        repo = HeadRepository(mock_connection_manager, mock_id_resolver)
        mock_id_resolver.resolve_id.return_value = 0

        result = repo.hard_delete(mock_conn=None, entity_id="Q42", head_revision_id=456)

        assert result.success is False
        assert "Entity Q42 not found" in result.error

    def test_hard_delete_db_error(self) -> None:
        """Test hard delete database error."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = HeadRepository(mock_connection_manager, mock_id_resolver)
        mock_id_resolver.resolve_id.return_value = 123
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB error")

        result = repo.hard_delete(mock_conn, "Q42", 456)

        assert result.success is False
        assert "DB error" in result.error

    def test_soft_delete_success(self) -> None:
        """Test successful soft delete."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = HeadRepository(mock_connection_manager, mock_id_resolver)
        mock_id_resolver.resolve_id.return_value = 123
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        result = repo.soft_delete(mock_conn, "Q42")

        assert result.success is True
        mock_cursor.execute.assert_called_once()

    def test_soft_delete_entity_not_found(self) -> None:
        """Test soft delete when entity not found."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()

        repo = HeadRepository(mock_connection_manager, mock_id_resolver)
        mock_id_resolver.resolve_id.return_value = 0

        result = repo.soft_delete(mock_conn=None, entity_id="Q42")

        assert result.success is False
        assert "Entity Q42 not found" in result.error

    def test_soft_delete_db_error(self) -> None:
        """Test soft delete database error."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = HeadRepository(mock_connection_manager, mock_id_resolver)
        mock_id_resolver.resolve_id.return_value = 123
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB error")

        result = repo.soft_delete(mock_conn, "Q42")

        assert result.success is False
        assert "DB error" in result.error

    def test_get_head_revision_success(self) -> None:
        """Test successful head revision retrieval."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = HeadRepository(mock_connection_manager, mock_id_resolver)
        mock_connection_manager.get_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (789,)

        result = repo.get_head_revision(123)

        assert result.success is True
        assert result.data == 789

    def test_get_head_revision_invalid_id(self) -> None:
        """Test head revision with invalid ID."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()

        repo = HeadRepository(mock_connection_manager, mock_id_resolver)

        result = repo.get_head_revision(0)

        assert result.success is False
        assert "Invalid internal entity ID" in result.error

    def test_get_head_revision_not_found(self) -> None:
        """Test head revision when entity not found."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = HeadRepository(mock_connection_manager, mock_id_resolver)
        mock_connection_manager.get_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        result = repo.get_head_revision(123)

        assert result.success is False
        assert "Entity not found" in result.error

    def test_get_head_revision_db_error(self) -> None:
        """Test head revision database error."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()

        repo = HeadRepository(mock_connection_manager, mock_id_resolver)
        mock_connection_manager.get_connection.side_effect = Exception("DB error")

        result = repo.get_head_revision(123)

        assert result.success is False
        assert "DB error" in result.error