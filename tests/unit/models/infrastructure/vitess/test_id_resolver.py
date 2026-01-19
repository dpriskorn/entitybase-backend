import pytest
from unittest.mock import MagicMock, patch

from models.infrastructure.vitess.id_resolver import IdResolver


class TestIdResolver:
    @pytest.fixture
    def mock_connection_manager(self):
        return MagicMock()

    @pytest.fixture
    def resolver(self, mock_connection_manager):
        return IdResolver(mock_connection_manager)

    def test_resolve_id_existing(self, resolver):
        """Test resolving an existing entity ID."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (12345,)

        result = IdResolver.resolve_id(mock_conn, "Q42")
        assert result == 12345

        mock_cursor.execute.assert_called_once_with(
            "SELECT internal_id FROM entity_id_mapping WHERE entity_id = %s",
            ("Q42",),
        )

    def test_resolve_id_nonexistent(self, resolver):
        """Test resolving a non-existent entity ID."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        result = IdResolver.resolve_id(mock_conn, "Q999")
        assert result == 0

    def test_entity_exists_true(self, resolver):
        """Test entity_exists returns True for existing entity."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (12345,)

        result = resolver.entity_exists(mock_conn, "Q42")
        assert result is True

    def test_entity_exists_false(self, resolver):
        """Test entity_exists returns False for non-existent entity."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        result = resolver.entity_exists(mock_conn, "Q999")
        assert result is False

    def test_resolve_entity_id_existing(self, resolver):
        """Test resolving an existing internal ID to entity ID."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = ("Q42",)

        result = IdResolver.resolve_entity_id(mock_conn, 12345)
        assert result == "Q42"

    def test_resolve_entity_id_nonexistent(self, resolver):
        """Test resolving a non-existent internal ID."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        result = IdResolver.resolve_entity_id(mock_conn, 99999)
        assert result == ""

    def test_register_entity_new(self, resolver, mock_connection_manager):
        """Test registering a new entity."""
        from unittest.mock import patch

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        # Mock entity_exists to return False
        with patch.object(resolver, 'entity_exists', return_value=False):
            with patch('models.infrastructure.unique_id.UniqueIdGenerator') as mock_gen:
                mock_gen.return_value.generate_unique_id.return_value = 54321
                resolver.register_entity(mock_conn, "Q100")

                mock_cursor.execute.assert_called_once_with(
                    "INSERT INTO entity_id_mapping (entity_id, internal_id) VALUES (%s, %s)",
                    ("Q100", 54321),
                )

    def test_register_entity_already_exists(self, resolver):
        """Test registering an entity that already exists (idempotent)."""
        mock_conn = MagicMock()

        # Mock entity_exists to return True
        with patch.object(resolver, 'entity_exists', return_value=True):
            resolver.register_entity(mock_conn, "Q100")

            # Should not execute insert
            mock_conn.cursor.assert_not_called()