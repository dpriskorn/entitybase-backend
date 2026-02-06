"""Unit tests for HeadRepository."""

from unittest.mock import MagicMock

from models.infrastructure.vitess.repositories.head import HeadRepository


class TestHeadRepository:
    """Unit tests for HeadRepository."""

    def test_cas_update_with_status_success(self):
        """Test successful CAS update with status flags."""
        from models.data.rest_api.v1.entitybase.request.entity.context import EntityHeadUpdateContext

        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.rowcount = 1
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = HeadRepository(vitess_client=mock_vitess_client)

        ctx = EntityHeadUpdateContext(
            entity_id="Q1",
            expected_head=10,
            new_head=11,
            is_semi_protected=True,
            is_locked=False,
            is_archived=False,
            is_dangling=False,
            is_mass_edit_protected=True,
            is_deleted=False,
            is_redirect=False,
        )
        result = repo.cas_update_with_status(ctx)

        assert result.success is True

    def test_cas_update_with_status_entity_not_found(self):
        """Test CAS update when entity not found."""
        from models.data.rest_api.v1.entitybase.request.entity.context import EntityHeadUpdateContext

        mock_vitess_client = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = None
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = HeadRepository(vitess_client=mock_vitess_client)

        ctx = EntityHeadUpdateContext(entity_id="Q999", expected_head=10, new_head=11)
        result = repo.cas_update_with_status(ctx)

        assert result.success is False
        assert "Entity not found" in result.error

    def test_cas_update_with_status_cas_failure(self):
        """Test CAS update when head mismatch."""
        from models.data.rest_api.v1.entitybase.request.entity.context import EntityHeadUpdateContext

        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.rowcount = 0  # No rows affected
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = HeadRepository(vitess_client=mock_vitess_client)

        ctx = EntityHeadUpdateContext(entity_id="Q1", expected_head=10, new_head=11)
        result = repo.cas_update_with_status(ctx)

        assert result.success is False
        assert "CAS failed" in result.error

    def test_cas_update_with_status_database_error(self):
        """Test CAS update with database error."""
        from models.data.rest_api.v1.entitybase.request.entity.context import EntityHeadUpdateContext

        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.execute.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = HeadRepository(vitess_client=mock_vitess_client)

        ctx = EntityHeadUpdateContext(entity_id="Q1", expected_head=10, new_head=11)
        result = repo.cas_update_with_status(ctx)

        assert result.success is False
        assert "DB error" in result.error

    def test_hard_delete_success(self):
        """Test successful hard delete."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = HeadRepository(vitess_client=mock_vitess_client)

        result = repo.hard_delete("Q1", 15)

        assert result.success is True

    def test_hard_delete_entity_not_found(self):
        """Test hard delete when entity not found."""
        mock_vitess_client = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = None
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = HeadRepository(vitess_client=mock_vitess_client)

        result = repo.hard_delete("Q999", 15)

        assert result.success is False
        assert "not found" in result.error

    def test_soft_delete_success(self):
        """Test successful soft delete."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = HeadRepository(vitess_client=mock_vitess_client)

        result = repo.soft_delete("Q1")

        assert result.success is True

    def test_soft_delete_entity_not_found(self):
        """Test soft delete when entity not found."""
        mock_vitess_client = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = None
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = HeadRepository(vitess_client=mock_vitess_client)

        result = repo.soft_delete("Q999")

        assert result.success is False
        assert "not found" in result.error

    def test_get_head_revision_success(self):
        """Test getting head revision successfully."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (15,)
        mock_vitess_client.cursor = mock_cursor

        repo = HeadRepository(vitess_client=mock_vitess_client)

        result = repo.get_head_revision(123)

        assert result.success is True
        assert result.data == 15

    def test_get_head_revision_entity_not_found(self):
        """Test getting head revision when entity not found."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_vitess_client.cursor = mock_cursor

        repo = HeadRepository(vitess_client=mock_vitess_client)

        result = repo.get_head_revision(123)

        assert result.success is False
        assert "Entity not found" in result.error

    def test_get_head_revision_invalid_id(self):
        """Test getting head revision with invalid ID."""
        mock_vitess_client = MagicMock()

        repo = HeadRepository(vitess_client=mock_vitess_client)

        result = repo.get_head_revision(0)

        assert result.success is False
        assert "Invalid internal entity ID" in result.error

    def test_get_head_revision_database_error(self):
        """Test getting head revision with database error."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = HeadRepository(vitess_client=mock_vitess_client)

        result = repo.get_head_revision(123)

        assert result.success is False
        assert "DB error" in result.error
