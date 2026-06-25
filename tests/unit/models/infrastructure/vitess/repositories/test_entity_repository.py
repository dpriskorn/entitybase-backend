"""Unit tests for EntityRepository."""

import pytest
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

    def test_is_archived_true(self):
        """Test checking if entity is archived."""
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

        result = repo.is_archived("Q123")

        assert result is True

    def test_is_archived_false(self):
        """Test checking if entity is not archived."""
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

        result = repo.is_archived("Q123")

        assert result is False

    def test_is_archived_entity_not_found(self):
        """Test is_archived for entity not found."""
        mock_vitess_client = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 0
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = EntityRepository(vitess_client=mock_vitess_client)

        result = repo.is_archived("Q999")

        assert result is False

    def test_get_protection_info_success(self):
        """Test getting protection info successfully."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchone.return_value = (True, False, True, False, True)
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = EntityRepository(vitess_client=mock_vitess_client)

        result = repo.get_protection_info("Q123")

        assert result is not None
        assert result.is_semi_protected is True
        assert result.is_locked is False
        assert result.is_archived is True
        assert result.is_dangling is False
        assert result.is_mass_edit_protected is True

    def test_get_protection_info_entity_not_found(self):
        """Test getting protection info when entity not found."""
        mock_vitess_client = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 0
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = EntityRepository(vitess_client=mock_vitess_client)

        result = repo.get_protection_info("Q999")

        assert result is None

    def test_get_protection_info_no_result(self):
        """Test getting protection info when no record exists."""
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

        result = repo.get_protection_info("Q123")

        assert result is None

    def test_create_entity_new(self):
        """Test creating a new entity."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.side_effect = [
            0,
            456,
        ]  # first not found, then found after register
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = EntityRepository(vitess_client=mock_vitess_client)

        repo.create_entity("Q123")

        mock_id_resolver.register_entity.assert_called_once_with("Q123")
        mock_cursor.execute.assert_called_once()

    def test_create_entity_already_exists(self):
        """Test creating an entity that already exists."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = EntityRepository(vitess_client=mock_vitess_client)

        repo.create_entity("Q123")

        mock_id_resolver.register_entity.assert_not_called()
        mock_cursor.execute.assert_called_once()

    def test_create_entity_register_fails(self):
        """Test creating entity when registration fails."""
        from fastapi import HTTPException

        mock_vitess_client = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.side_effect = [0, 0]  # not found both times
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = EntityRepository(vitess_client=mock_vitess_client)

        with pytest.raises(HTTPException, match="Failed to register entity"):
            repo.create_entity("Q123")

    def test_delete_entity_success(self):
        """Test deleting an entity."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = EntityRepository(vitess_client=mock_vitess_client)

        repo.delete_entity("Q123")

        mock_cursor.execute.assert_called_once_with(
            "DELETE FROM entity_head WHERE internal_id = %s", (123,)
        )

    def test_delete_entity_not_found(self):
        """Test deleting an entity that doesn't exist."""
        mock_vitess_client = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 0
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = EntityRepository(vitess_client=mock_vitess_client)

        repo.delete_entity("Q999")

        # Should not call cursor.execute
        mock_vitess_client.cursor = None  # verify cursor not accessed

    def test_list_entities_filtered_with_status(self):
        """Test listing entities filtered by status."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchall.return_value = [
            ("Q123", 456),
        ]
        mock_vitess_client.cursor = mock_cursor

        repo = EntityRepository(vitess_client=mock_vitess_client)

        filter_request = EntityFilterRequest(
            entity_type="",
            status="locked",
            edit_type="",
            limit=100,
            offset=0,
        )

        result = repo.list_entities_filtered(filter_request)

        assert len(result) == 1
        assert result[0].entity_id == "Q123"

    def test_list_entities_filtered_invalid_status(self):
        """Test listing entities with invalid status returns empty."""
        mock_vitess_client = MagicMock()

        repo = EntityRepository(vitess_client=mock_vitess_client)

        filter_request = EntityFilterRequest(
            entity_type="",
            status="invalid_status",
            edit_type="",
            limit=100,
            offset=0,
        )

        result = repo.list_entities_filtered(filter_request)

        assert result == []

    def test_list_entities_filtered_with_all_filters(self):
        """Test listing entities with all filters combined."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchall.return_value = [
            ("Q123", 456, "manual_update", 100),
        ]
        mock_vitess_client.cursor = mock_cursor

        repo = EntityRepository(vitess_client=mock_vitess_client)

        filter_request = EntityFilterRequest(
            entity_type="item",
            status="locked",
            edit_type="manual_update",
            limit=100,
            offset=0,
        )

        result = repo.list_entities_filtered(filter_request)

        assert len(result) == 1
        assert result[0].entity_id == "Q123"
        assert result[0].edit_type == "manual_update"
        assert result[0].revision_id == 100
