"""Unit tests for LexemeRepository."""

from models.infrastructure.vitess.repositories.lexeme_repository import LexemeRepository


class TestLexemeRepository:
    """Unit tests for LexemeRepository."""

    def test_store_lexeme_terms_success(self):
        """Test storing lexeme terms successfully."""
        # Since it's a placeholder, just ensure no exceptions
        repo = LexemeRepository()

        term_hashes = {
            "forms": {
                "L42-F1": {"en": "hash1", "de": "hash2"}
            },
            "senses": {
                "L42-S1": {"en": "hash3", "de": "hash4"}
            }
        }

        # Should not raise any exceptions
        repo.store_lexeme_terms("L42", term_hashes)

    def test_store_lexeme_terms_empty(self):
        """Test storing empty term hashes."""
        repo = LexemeRepository()

        term_hashes = {"forms": {}, "senses": {}}

        repo.store_lexeme_terms("L42", term_hashes)

    def test_get_lexeme_terms_success(self):
        """Test retrieving lexeme terms."""
        repo = LexemeRepository()

        result = repo.get_lexeme_terms("L42")

        expected = {"forms": {}, "senses": {}}
        assert result == expected

    def test_get_lexeme_terms_different_entity(self):
        """Test retrieving terms for different entity."""
        repo = LexemeRepository()

        result1 = repo.get_lexeme_terms("L42")
        result2 = repo.get_lexeme_terms("L43")

        # Currently returns static data, so same result
        assert result1 == result2
        assert result1 == {"forms": {}, "senses": {}}

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