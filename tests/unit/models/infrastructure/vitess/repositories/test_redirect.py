"""Unit tests for RedirectRepository."""

import pytest
from unittest.mock import MagicMock

from models.infrastructure.vitess.repositories.redirect import RedirectRepository


class TestRedirectRepository:
    """Unit tests for RedirectRepository."""

    def test_set_target_success(self):
        """Test successful redirect target setting."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.side_effect = [123, 456]  # from, to
        mock_cursor.rowcount = 1
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = RedirectRepository(vitess_client=mock_vitess_client)

        result = repo.set_target("Q1", "Q2")

        assert result.success is True

    def test_set_target_entity_not_found(self):
        """Test setting target when entity not found."""
        mock_vitess_client = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = None
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = RedirectRepository(vitess_client=mock_vitess_client)

        result = repo.set_target("Q999", "Q2")

        assert result.success is False
        assert "not found" in result.error

    def test_set_target_cas_failure(self):
        """Test CAS failure in set_target."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.side_effect = [123, 456]
        mock_cursor.rowcount = 0  # no rows affected
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = RedirectRepository(vitess_client=mock_vitess_client)

        result = repo.set_target("Q1", "Q2", expected_redirects_to=789)

        assert result.success is False
        assert "CAS failed" in result.error

    def test_create_success(self):
        """Test successful redirect creation."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.side_effect = [123, 456]
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = RedirectRepository(vitess_client=mock_vitess_client)

        repo.create("Q1", "Q2")

        mock_cursor.execute.assert_called_once()

    def test_create_source_not_found(self):
        """Test redirect creation when source not found."""
        mock_vitess_client = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = None
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = RedirectRepository(vitess_client=mock_vitess_client)

        with pytest.raises(Exception):  # raise_validation_error
            repo.create("Q999", "Q2")

    def test_get_incoming_redirects_success(self):
        """Test getting incoming redirects."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchall.return_value = [("Q1",), ("Q2",)]
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = RedirectRepository(vitess_client=mock_vitess_client)

        result = repo.get_incoming_redirects("Q3")

        assert result == ["Q1", "Q2"]

    def test_get_incoming_redirects_entity_not_found(self):
        """Test getting redirects when entity not found."""
        mock_vitess_client = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = None
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = RedirectRepository(vitess_client=mock_vitess_client)

        result = repo.get_incoming_redirects("Q999")

        assert result == []

    def test_get_target_found(self):
        """Test getting redirect target when exists."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchone.return_value = ("Q2",)
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = RedirectRepository(vitess_client=mock_vitess_client)

        result = repo.get_target("Q1")

        assert result == "Q2"

    def test_get_target_not_found(self):
        """Test getting target when no redirect exists."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchone.return_value = None
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = RedirectRepository(vitess_client=mock_vitess_client)

        result = repo.get_target("Q1")

        assert result == ""
