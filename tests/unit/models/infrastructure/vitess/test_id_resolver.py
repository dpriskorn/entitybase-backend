"""Unit tests for id_resolver."""

from unittest.mock import MagicMock, patch

from models.infrastructure.vitess.id_resolver import IdResolver


class TestIdResolver:
    """Unit tests for IdResolver."""

    def setup_method(self):
        """Set up test fixtures."""
        self.vitess_client = MagicMock()
        self.resolver = IdResolver(vitess_client=self.vitess_client)

    def test_resolve_id_found(self):
        """Test resolving ID when entity exists."""
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=None)
        mock_cursor.fetchone.return_value = (123,)
        self.vitess_client.cursor = mock_cursor

        result = self.resolver.resolve_id("Q42")

        assert result == 123
        mock_cursor.execute.assert_called_once_with(
            "SELECT internal_id FROM entity_id_mapping WHERE entity_id = %s",
            ("Q42",),
        )

    def test_resolve_id_not_found(self):
        """Test resolving ID when entity doesn't exist."""
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=None)
        mock_cursor.fetchone.return_value = None
        self.vitess_client.cursor = mock_cursor

        result = self.resolver.resolve_id("Q999")

        assert result == 0

    def test_entity_exists_true(self):
        """Test entity_exists returns True when entity exists."""
        with patch.object(self.resolver, 'resolve_id', return_value=456):
            result = self.resolver.entity_exists("Q42")

            assert result is True

    def test_entity_exists_false(self):
        """Test entity_exists returns False when entity doesn't exist."""
        with patch.object(self.resolver, 'resolve_id', return_value=0):
            result = self.resolver.entity_exists("Q999")

            assert result is False

    def test_resolve_entity_id_found(self):
        """Test resolving entity ID when internal ID exists."""
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=None)
        mock_cursor.fetchone.return_value = ("Q42",)
        self.vitess_client.cursor = mock_cursor

        result = self.resolver.resolve_entity_id(123)

        assert result == "Q42"
        mock_cursor.execute.assert_called_once_with(
            "SELECT entity_id FROM entity_id_mapping WHERE internal_id = %s",
            (123,),
        )

    def test_resolve_entity_id_not_found(self):
        """Test resolving entity ID when internal ID doesn't exist."""
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=None)
        mock_cursor.fetchone.return_value = None
        self.vitess_client.cursor = mock_cursor

        result = self.resolver.resolve_entity_id(999)

        assert result == ""

    @patch('models.infrastructure.vitess.id_resolver.UniqueIdGenerator')
    def test_register_entity_new(self, mock_generator_class):
        """Test registering a new entity."""
        mock_generator = MagicMock()
        mock_generator.generate_unique_id.return_value = 789
        mock_generator_class.return_value = mock_generator

        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=None)
        self.vitess_client.cursor = mock_cursor

        with patch.object(self.resolver, 'entity_exists', return_value=False):
            self.resolver.register_entity("Q42")

            mock_cursor.execute.assert_called_once_with(
                "INSERT INTO entity_id_mapping (entity_id, internal_id) VALUES (%s, %s)",
                ("Q42", 789),
            )

    @patch('models.infrastructure.vitess.id_resolver.UniqueIdGenerator')
    def test_register_entity_already_exists(self, mock_generator_class):
        """Test registering an entity that already exists."""
        with patch.object(self.resolver, 'entity_exists', return_value=True):
            self.resolver.register_entity("Q42")

            # Should not generate ID or insert
            mock_generator_class.assert_not_called()
