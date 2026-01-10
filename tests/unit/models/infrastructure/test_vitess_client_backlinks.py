from unittest.mock import Mock, patch
from typing import Union
from models.infrastructure.vitess_client import VitessClient
from models.vitess_models import VitessConfig


class TestVitessClientBacklinks:
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.config = VitessConfig(
            host="localhost", port=3306, database="test", user="test", password="test"
        )
        with (
            patch("models.infrastructure.vitess_client.VitessConnectionManager"),
            patch("models.infrastructure.vitess_client.SchemaManager"),
            patch("models.infrastructure.vitess_client.IdResolver"),
            patch("models.infrastructure.vitess_client.EntityRepository"),
            patch("models.infrastructure.vitess_client.RevisionRepository"),
            patch("models.infrastructure.vitess_client.RedirectRepository"),
            patch("models.infrastructure.vitess_client.HeadRepository"),
            patch("models.infrastructure.vitess_client.StatementRepository"),
            patch("models.infrastructure.vitess_client.BacklinkRepository"),
        ):
            self.vitess_client = VitessClient(self.config)

    def test_insert_backlinks(self) -> None:
        """Test insert_backlinks delegates to repository."""
        backlinks: list[tuple[int, int, int, str, str]] = [
            (123, 456, 789, "P31", "normal")
        ]

        mock_conn = Mock()
        self.vitess_client.connection_manager.get_connection.return_value.__enter__.return_value = mock_conn

        self.vitess_client.insert_backlinks(backlinks)

        self.vitess_client.backlink_repository.insert_backlinks.assert_called_once_with(
            mock_conn, backlinks
        )

    def test_insert_backlinks_empty_list(self) -> None:
        """Test insert_backlinks handles empty list."""
        backlinks: list[tuple[int, int, int, str, str]] = []

        self.vitess_client.insert_backlinks(backlinks)

        # Should still get connection but repository not called
        self.vitess_client.connection_manager.get_connection.assert_called_once()
        self.vitess_client.backlink_repository.insert_backlinks.assert_called_once_with(
            self.vitess_client.connection_manager.get_connection.return_value.__enter__.return_value,
            backlinks,
        )

    def test_delete_backlinks_for_entity(self) -> None:
        """Test delete_backlinks_for_entity delegates to repository."""
        referencing_internal_id = 456

        mock_conn = Mock()
        self.vitess_client.connection_manager.get_connection.return_value.__enter__.return_value = mock_conn

        self.vitess_client.delete_backlinks_for_entity(referencing_internal_id)

        self.vitess_client.backlink_repository.delete_backlinks_for_entity.assert_called_once_with(
            mock_conn, referencing_internal_id
        )

    def test_get_backlinks(self) -> None:
        """Test get_backlinks delegates to repository and returns results."""
        referenced_internal_id = 123
        mock_results: list[dict[str, Union[int, str]]] = [
            {
                "referencing_internal_id": 456,
                "statement_hash": 789,
                "property_id": "P31",
                "rank": "normal",
            }
        ]

        mock_conn = Mock()
        self.vitess_client.connection_manager.get_connection.return_value.__enter__.return_value = mock_conn
        self.vitess_client.backlink_repository.get_backlinks.return_value = mock_results

        result = self.vitess_client.get_backlinks(referenced_internal_id)

        self.vitess_client.backlink_repository.get_backlinks.assert_called_once_with(
            mock_conn, referenced_internal_id, 100, 0
        )
        assert result == mock_results

    def test_get_backlinks_with_pagination(self) -> None:
        """Test get_backlinks with custom pagination."""
        referenced_internal_id = 123
        limit = 50
        offset = 25
        mock_results: list[dict[str, Union[int, str]]] = []

        mock_conn = Mock()
        self.vitess_client.connection_manager.get_connection.return_value.__enter__.return_value = mock_conn
        self.vitess_client.backlink_repository.get_backlinks.return_value = mock_results

        result = self.vitess_client.get_backlinks(referenced_internal_id, limit, offset)

        self.vitess_client.backlink_repository.get_backlinks.assert_called_once_with(
            mock_conn, referenced_internal_id, limit, offset
        )
        assert result == mock_results

    def test_connection_context_management(self) -> None:
        """Test that connections are properly managed with context managers."""
        backlinks: list[tuple[int, int, int, str, str]] = [
            (123, 456, 789, "P31", "normal")
        ]

        mock_conn_manager = self.vitess_client.connection_manager
        mock_conn = Mock()
        mock_conn_manager.get_connection.return_value.__enter__.return_value = mock_conn
        mock_conn_manager.get_connection.return_value.__exit__.return_value = None

        self.vitess_client.insert_backlinks(backlinks)

        mock_conn_manager.get_connection.assert_called_once()
        mock_conn_manager.get_connection.return_value.__enter__.assert_called_once()
        mock_conn_manager.get_connection.return_value.__exit__.assert_called_once()

    def test_repository_initialization(self) -> None:
        """Test that BacklinkRepository is properly initialized."""
        with patch("models.infrastructure.vitess_client.VitessConnectionManager"):
            client = VitessClient(self.config)
            assert client.backlink_repository is not None
            # Verify it was created with the connection manager
            assert isinstance(client.backlink_repository.connection_manager, Mock)
