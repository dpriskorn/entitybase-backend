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
            "forms": {
                "L42-F1": {"en": 123, "de": 456}
            },
            "senses": {
                "L42-S1": {"en": 789, "de": 101}
            }
        }

        repo.store_lexeme_terms("L42", term_hashes)

        # Verify DELETE was called
        mock_cursor.execute.assert_any_call(
            "DELETE FROM lexeme_terms WHERE entity_id = %s",
            ("L42",)
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
            "DELETE FROM lexeme_terms WHERE entity_id = %s",
            ("L42",)
        )

    def test_get_lexeme_terms_success(self):
        """Test retrieving lexeme terms."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.__enter__ = MagicMock(return_value=mock_cursor)
        mock_cursor.__exit__ = MagicMock(return_value=None)
        mock_cursor.fetchall.return_value = [
            ("L42-F1", "form", "en", 123),
            ("L42-F1", "form", "de", 456),
            ("L42-S1", "sense", "en", 789)
        ]
        mock_vitess_client.cursor = mock_cursor

        repo = LexemeRepository(vitess_client=mock_vitess_client)

        result = repo.get_lexeme_terms("L42")

        expected = {
            "forms": {"L42-F1": {"en": 123, "de": 456}},
            "senses": {"L42-S1": {"en": 789}}
        }
        assert result == expected

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

        assert result1 == result2
        assert result1 == {"forms": {}, "senses": {}}

        # Verify different entity IDs were queried
        calls = [call[0][1][0] for call in mock_cursor.execute.call_args_list]
        assert "L42" in calls
        assert "L43" in calls

    def test_store_lexeme_terms_complex(self):
        """Test storing complex term hashes."""
        repo = LexemeRepository()

        term_hashes = {
            "forms": {
                "L42-F1": {"en": "hash1", "de": "hash2", "fr": "hash3"},
                "L42-F2": {"en": "hash4"}
            },
            "senses": {
                "L42-S1": {"en": "hash5", "de": "hash6"},
                "L42-S2": {"en": "hash7", "es": "hash8"}
            }
        }

        # Should not raise
        repo.store_lexeme_terms("L42", term_hashes)

    def test_get_lexeme_terms_invalid_entity(self):
        """Test retrieving terms for invalid entity ID."""
        repo = LexemeRepository()

        # Should work for any string currently
        result = repo.get_lexeme_terms("invalid")

        assert result == {"forms": {}, "senses": {}}

    def test_store_lexeme_terms_none_values(self):
        """Test storing with None values."""
        repo = LexemeRepository()

        term_hashes = None

        # Should handle gracefully (placeholder)
        repo.store_lexeme_terms("L42", term_hashes)

    def test_get_lexeme_terms_empty_entity(self):
        """Test retrieving for empty entity ID."""
        repo = LexemeRepository()

        result = repo.get_lexeme_terms("")

        assert result == {"forms": {}, "senses": {}}

    def test_store_lexeme_terms_logging(self, caplog):
        """Test that storing lexeme terms logs debug message."""
        import logging
        caplog.set_level(logging.DEBUG)
        repo = LexemeRepository()

        term_hashes = {"forms": {}, "senses": {}}

        repo.store_lexeme_terms("L42", term_hashes)

        assert "Storing lexeme terms for L42" in caplog.text

    def test_get_lexeme_terms_logging(self, caplog):
        """Test that retrieving lexeme terms logs debug message."""
        import logging
        caplog.set_level(logging.DEBUG)
        repo = LexemeRepository()

        result = repo.get_lexeme_terms("L42")

        assert "Retrieving lexeme terms for L42" in caplog.text
        assert result == {"forms": {}, "senses": {}}