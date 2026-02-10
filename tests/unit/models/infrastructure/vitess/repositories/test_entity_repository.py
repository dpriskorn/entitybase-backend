"""Unit tests for EntityRepository."""

from unittest.mock import MagicMock

from models.infrastructure.vitess.repositories.entity import EntityRepository
from models.data.rest_api.v1.entitybase.request.entity_filter import EntityFilterRequest


class TestEntityRepository:
    """Unit tests for EntityRepository."""

    def test_get_head_found(self):
        """Test getting head revision when entity exists."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchone.return_value = (456,)
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = EntityRepository(vitess_client=mock_vitess_client)

        result = repo.get_head("Q123")

        assert result == 456

    def test_get_head_not_found(self):
        """Test getting head revision when entity not found."""
        mock_vitess_client = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = None
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = EntityRepository(vitess_client=mock_vitess_client)

        result = repo.get_head("Q999")

        assert result == 0

    def test_get_head_no_head_record(self):
        """Test getting head when no record exists."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchone.return_value = None
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = EntityRepository(vitess_client=mock_vitess_client)

        result = repo.get_head("Q123")

        assert result == 0

    def test_is_deleted_true(self):
        """Test checking if entity is deleted."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchone.return_value = (True,)
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = EntityRepository(vitess_client=mock_vitess_client)

        result = repo.is_deleted("Q123")

        assert result is True

    def test_is_deleted_false(self):
        """Test checking if entity is not deleted."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchone.return_value = (False,)
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = EntityRepository(vitess_client=mock_vitess_client)

        result = repo.is_deleted("Q123")

        assert result is False

    def test_is_locked_true(self):
        """Test checking if entity is locked."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchone.return_value = (True,)
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = EntityRepository(vitess_client=mock_vitess_client)

        result = repo.is_locked("Q123")

        assert result is True

    def test_get_head_entity_not_found(self):
        """Test getting head for entity not found."""
        mock_vitess_client = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = None
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = EntityRepository(vitess_client=mock_vitess_client)

        result = repo.get_head("Q999")

        assert result == 0

    def test_is_deleted_entity_not_found(self):
        """Test is_deleted for entity not found."""
        mock_vitess_client = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = None
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = EntityRepository(vitess_client=mock_vitess_client)

        result = repo.is_deleted("Q999")

        assert result is False

    def test_is_locked_entity_not_found(self):
        """Test is_locked for entity not found."""
        mock_vitess_client = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = None
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = EntityRepository(vitess_client=mock_vitess_client)

        result = repo.is_locked("Q999")

        assert result is False

    def test_list_entities_filtered_with_entity_type(self):
        """Test listing entities filtered by entity type."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchall.return_value = [
            ("Q123", 456),
            ("Q456", 789),
        ]
        mock_vitess_client.cursor = mock_cursor

        repo = EntityRepository(vitess_client=mock_vitess_client)

        filter_request = EntityFilterRequest(
            entity_type="item",
            status="",
            edit_type="",
            limit=100,
            offset=0,
        )

        result = repo.list_entities_filtered(filter_request)

        assert len(result) == 2
        assert result[0].entity_id == "Q123"
        assert result[0].head_revision_id == 456

    def test_list_entities_filtered_with_edit_type(self):
        """Test listing entities filtered by edit type."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchall.return_value = [
            ("Q123", 456, "mass_edit", 100),
        ]
        mock_vitess_client.cursor = mock_cursor

        repo = EntityRepository(vitess_client=mock_vitess_client)

        filter_request = EntityFilterRequest(
            entity_type="",
            status="",
            edit_type="mass_edit",
            limit=100,
            offset=0,
        )

        result = repo.list_entities_filtered(filter_request)

        assert len(result) == 1
        assert result[0].entity_id == "Q123"
        assert result[0].head_revision_id == 456
        assert result[0].edit_type == "mass_edit"
        assert result[0].revision_id == 100
