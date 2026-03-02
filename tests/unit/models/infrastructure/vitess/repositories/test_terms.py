"""Unit tests for TermsRepository."""

from unittest.mock import MagicMock

from models.infrastructure.vitess.repositories.terms import TermsRepository


class TestTermsRepository:
    """Unit tests for TermsRepository."""

    def test_insert_term_success(self):
        """Test inserting term successfully."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_vitess_client.cursor = mock_cursor

        repo = TermsRepository(vitess_client=mock_vitess_client)

        result = repo.insert_term(12345, "test term", "label")

        assert result.success is True

    def test_insert_term_invalid_hash(self):
        """Test inserting term with invalid hash."""
        mock_vitess_client = MagicMock()

        repo = TermsRepository(vitess_client=mock_vitess_client)

        result = repo.insert_term(0, "test term", "label")

        assert result.success is False
        assert "Invalid hash value" in result.error

    def test_insert_term_database_error(self):
        """Test inserting term with database error."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.execute.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = TermsRepository(vitess_client=mock_vitess_client)

        result = repo.insert_term(12345, "test term", "label")

        assert result.success is False
        assert "DB error" in result.error

    def test_increment_ref_count_success(self):
        """Test incrementing ref_count successfully."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchone.return_value = (5,)
        mock_vitess_client.cursor = mock_cursor

        repo = TermsRepository(vitess_client=mock_vitess_client)

        result = repo.increment_ref_count(12345)

        assert result.success is True
        assert result.data == 5

    def test_increment_ref_count_invalid_hash(self):
        """Test incrementing ref_count with invalid hash."""
        mock_vitess_client = MagicMock()

        repo = TermsRepository(vitess_client=mock_vitess_client)

        result = repo.increment_ref_count(0)

        assert result.success is False
        assert "Invalid hash value" in result.error

    def test_decrement_ref_count_success(self):
        """Test decrementing ref_count successfully."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchone.return_value = (4,)
        mock_vitess_client.cursor = mock_cursor

        repo = TermsRepository(vitess_client=mock_vitess_client)

        result = repo.decrement_ref_count(12345)

        assert result.success is True
        assert result.data == 4

    def test_decrement_ref_count_invalid_hash(self):
        """Test decrementing ref_count with invalid hash."""
        mock_vitess_client = MagicMock()

        repo = TermsRepository(vitess_client=mock_vitess_client)

        result = repo.decrement_ref_count(-1)

        assert result.success is False
        assert "Invalid hash value" in result.error

    def test_get_ref_count_found(self):
        """Test getting ref_count when term exists."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchone.return_value = (10,)
        mock_vitess_client.cursor = mock_cursor

        repo = TermsRepository(vitess_client=mock_vitess_client)

        result = repo.get_ref_count(12345)

        assert result == 10

    def test_get_ref_count_not_found(self):
        """Test getting ref_count when term doesn't exist."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchone.return_value = None
        mock_vitess_client.cursor = mock_cursor

        repo = TermsRepository(vitess_client=mock_vitess_client)

        result = repo.get_ref_count(12345)

        assert result == 0

    def test_get_ref_count_invalid_hash(self):
        """Test getting ref_count with invalid hash."""
        mock_vitess_client = MagicMock()

        repo = TermsRepository(vitess_client=mock_vitess_client)

        result = repo.get_ref_count(0)

        assert result == 0

    def test_get_orphaned_success(self):
        """Test getting orphaned terms."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_cursor.fetchall.return_value = [
            (12345, "label"),
            (67890, "description"),
        ]
        mock_vitess_client.cursor = mock_cursor

        repo = TermsRepository(vitess_client=mock_vitess_client)

        result = repo.get_orphaned(older_than_days=1, limit=100)

        assert result.success is True
        assert result.data == [(12345, "label"), (67890, "description")]

    def test_get_orphaned_invalid_params(self):
        """Test getting orphaned terms with invalid params."""
        mock_vitess_client = MagicMock()

        repo = TermsRepository(vitess_client=mock_vitess_client)

        result = repo.get_orphaned(older_than_days=0, limit=100)

        assert result.success is False
        assert "Invalid parameters" in result.error

    def test_delete_term(self):
        """Test deleting a term."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=False)
        mock_vitess_client.cursor = mock_cursor

        repo = TermsRepository(vitess_client=mock_vitess_client)

        repo.delete_term(12345)

        mock_cursor.execute.assert_called_once()
