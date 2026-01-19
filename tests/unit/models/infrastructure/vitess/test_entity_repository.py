import pytest
from unittest.mock import MagicMock, patch

pytestmark = pytest.mark.unit

from models.infrastructure.vitess.repositories.entity import EntityRepository


class TestEntityRepository:
    def test_init(self) -> None:
        """Test EntityRepository initialization."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()

        repo = EntityRepository(mock_connection_manager, mock_id_resolver)

        assert repo.connection_manager == mock_connection_manager
        assert repo.id_resolver == mock_id_resolver

    def test_create_entity_success_registered(self) -> None:
        """Test successful entity creation when already registered."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = EntityRepository(mock_connection_manager, mock_id_resolver)
        mock_id_resolver.resolve_id.return_value = 123
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        repo.create_entity(mock_conn, "Q42")

        # Verify register_entity was not called since already registered
        mock_id_resolver.register_entity.assert_not_called()
        # Verify INSERT was executed
        mock_cursor.execute.assert_called_once()

    def test_create_entity_success_unregistered(self) -> None:
        """Test successful entity creation when not registered - should register first."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = EntityRepository(mock_connection_manager, mock_id_resolver)
        # First resolve_id returns 0 (not registered)
        mock_id_resolver.resolve_id.side_effect = [0, 456]  # First call 0, second call 456 after register
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        repo.create_entity(mock_conn, "Q300000000")

        # Verify register_entity was called
        mock_id_resolver.register_entity.assert_called_once_with(mock_conn, "Q300000000")
        # Verify resolve_id was called twice: first to check, second after register
        assert mock_id_resolver.resolve_id.call_count == 2
        # Verify INSERT was executed
        mock_cursor.execute.assert_called_once()

    @patch("models.infrastructure.vitess.repositories.entity.raise_validation_error")
    def test_create_entity_register_fails(self, mock_raise) -> None:
        """Test entity creation fails if registration doesn't work."""
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()
        mock_conn = MagicMock()

        repo = EntityRepository(mock_connection_manager, mock_id_resolver)
        # First resolve_id returns 0, second also 0 (register failed)
        mock_id_resolver.resolve_id.return_value = 0

        repo.create_entity(mock_conn, "Q999")

        # Verify register_entity was called
        mock_id_resolver.register_entity.assert_called_once_with(mock_conn, "Q999")
        # Verify raise_validation_error was called with new message
        mock_raise.assert_called_once_with(
            "Failed to register entity Q999", status_code=500
        )

    @patch("models.infrastructure.vitess.repositories.entity.raise_validation_error")
    def test_create_entity_old_behavior_fails(self, mock_raise) -> None:
        """Test that the old behavior (raising error for unregistered) is no longer present."""
        # This test ensures our change removed the old error
        mock_connection_manager = MagicMock()
        mock_id_resolver = MagicMock()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        repo = EntityRepository(mock_connection_manager, mock_id_resolver)
        # Mock successful registration
        mock_id_resolver.resolve_id.side_effect = [0, 789]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        repo.create_entity(mock_conn, "Q300000000")

        # Should not raise the old error
        mock_raise.assert_not_called()
        # Should have registered and created
        mock_id_resolver.register_entity.assert_called_once()
        mock_cursor.execute.assert_called_once()</content>
<parameter name="filePath">/home/dpriskorn/src/python/wikibase-backend/tests/unit/models/infrastructure/vitess/test_entity_repository.py