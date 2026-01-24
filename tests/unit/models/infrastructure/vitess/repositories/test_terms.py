"""Unit tests for TermsRepository."""

from unittest.mock import MagicMock

from models.infrastructure.vitess.repositories.terms import TermsRepository
from models.data.rest_api.v1.entitybase.response import TermsResponse


class TestTermsRepository:
    """Unit tests for TermsRepository."""

    def test_insert_term_success(self):
        """Test inserting term successfully."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_vitess_client.cursor = mock_cursor

        repo = TermsRepository(vitess_client=mock_vitess_client)

        result = repo.insert_term(12345, "test term", "label")

        assert result.success is True

    def test_insert_term_database_error(self):
        """Test inserting term with database error."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = TermsRepository(vitess_client=mock_vitess_client)

        result = repo.insert_term(12345, "test term", "label")

        assert result.success is False
        assert "DB error" in result.error

    def test_get_term_found(self):
        """Test getting term when it exists."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("test term", "label")
        mock_vitess_client.cursor = mock_cursor

        repo = TermsRepository(vitess_client=mock_vitess_client)

        result = repo.get_term(12345)

        assert result == ("test term", "label")

    def test_get_term_not_found(self):
        """Test getting term when it doesn't exist."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_vitess_client.cursor = mock_cursor

        repo = TermsRepository(vitess_client=mock_vitess_client)

        result = repo.get_term(12345)

        assert result is None

    def test_batch_get_terms_success(self):
        """Test batch getting terms successfully."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (12345, "term1", "label"),
            (67890, "term2", "alias")
        ]
        mock_vitess_client.cursor = mock_cursor

        repo = TermsRepository(vitess_client=mock_vitess_client)

        result = repo.batch_get_terms([12345, 67890])

        assert isinstance(result, TermsResponse)
        assert 12345 in result.terms
        assert 67890 in result.terms
        assert result.terms[12345] == ("term1", "label")

    def test_batch_get_terms_empty_list(self):
        """Test batch getting terms with empty list."""
        mock_vitess_client = MagicMock()

        repo = TermsRepository(vitess_client=mock_vitess_client)

        result = repo.batch_get_terms([])

        assert isinstance(result, TermsResponse)
        assert result.terms == {}

    def test_batch_get_terms_partial_results(self):
        """Test batch getting terms with some not found."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            (12345, "term1", "label")
            # 67890 not found
        ]
        mock_vitess_client.cursor = mock_cursor

        repo = TermsRepository(vitess_client=mock_vitess_client)

        result = repo.batch_get_terms([12345, 67890])

        assert isinstance(result, TermsResponse)
        assert 12345 in result.terms
        assert 67890 not in result.terms

    def test_hash_exists_true(self):
        """Test checking if hash exists when it does."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1,)
        mock_vitess_client.cursor = mock_cursor

        repo = TermsRepository(vitess_client=mock_vitess_client)

        result = repo.hash_exists(12345)

        assert result is True

    def test_hash_exists_false(self):
        """Test checking if hash exists when it doesn't."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_vitess_client.cursor = mock_cursor

        repo = TermsRepository(vitess_client=mock_vitess_client)

        result = repo.hash_exists(12345)

        assert result is False
