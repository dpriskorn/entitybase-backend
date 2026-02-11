"""Unit tests for LexemeRepository."""

from unittest.mock import MagicMock

from models.infrastructure.vitess.repositories.lexeme_repository import LexemeRepository


class TestLexemeRepository:
    """Unit tests for LexemeRepository."""

    def test_store_lexeme_terms_success(self):
        """Test storing lexeme terms successfully."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=None)
        mock_vitess_client.cursor = mock_cursor

        repo = LexemeRepository(vitess_client=mock_vitess_client)

        term_hashes = {
            "forms": {"L42-F1": {"en": 123, "de": 456}},
            "senses": {"L42-S1": {"en": 789, "de": 101}},
        }

        repo.store_lexeme_terms("L42", term_hashes)

        # Verify DELETE was called
        mock_cursor.execute.assert_any_call(
            "DELETE FROM lexeme_terms WHERE entity_id = %s", ("L42",)
        )

        # Verify INSERTs for forms
        assert mock_cursor.execute.call_count == 5  # DELETE + 2 forms + 2 senses

    def test_store_lexeme_terms_empty(self):
        """Test storing empty term hashes."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=None)
        mock_vitess_client.cursor = mock_cursor

        repo = LexemeRepository(vitess_client=mock_vitess_client)

        term_hashes = {"forms": {}, "senses": {}}

        repo.store_lexeme_terms("L42", term_hashes)

        # Only DELETE should be called
        mock_cursor.execute.assert_called_once_with(
            "DELETE FROM lexeme_terms WHERE entity_id = %s", ("L42",)
        )

    def test_get_lexeme_terms_different_entity(self):
        """Test retrieving terms for different entity."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=None)
        mock_cursor.fetchall.return_value = []
        mock_vitess_client.cursor = mock_cursor

        repo = LexemeRepository(vitess_client=mock_vitess_client)

        result1 = repo.get_lexeme_terms("L42")
        result2 = repo.get_lexeme_terms("L43")

        assert result1.model_dump() == result2.model_dump()
        assert result1.model_dump() == {"forms": {}, "senses": {}}

        # Verify different entity IDs were queried
        calls = [call[0][1][0] for call in mock_cursor.execute.call_args_list]
        assert "L42" in calls
        assert "L43" in calls
