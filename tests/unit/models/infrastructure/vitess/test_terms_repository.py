import unittest
from unittest.mock import Mock
from models.infrastructure.vitess.repositories.terms import TermsRepository
from models.rest_api.entitybase.v1.response.misc import TermsResponse


class TestTermsRepository(unittest.TestCase):
    """Unit tests for TermsRepository"""

    def setUp(self) -> None:
        """Set up test fixtures"""
        self.mock_connection_manager = Mock()
        self.mock_conn = Mock()
        self.mock_cursor = Mock()
        self.terms_repo = TermsRepository(self.mock_connection_manager)

        # Set up the context manager mocks
        self.mock_connection_manager.get_connection.return_value.__enter__ = Mock(
            return_value=self.mock_conn
        )
        self.mock_connection_manager.get_connection.return_value.__exit__ = Mock(
            return_value=None
        )
        self.mock_conn.cursor.return_value.__enter__ = Mock(
            return_value=self.mock_cursor
        )
        self.mock_conn.cursor.return_value.__exit__ = Mock(return_value=None)

    def test_insert_term_new(self) -> None:
        """Test inserting a new term"""
        self.terms_repo.insert_term(12345, "test term", "label")

        self.mock_cursor.execute.assert_called_once_with(
            """
                    INSERT INTO entity_terms (hash, term, term_type)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE hash = hash
                    """,
            (12345, "test term", "label"),
        )

    def test_get_term_found(self) -> None:
        """Test getting an existing term"""
        self.mock_cursor.fetchone.return_value = ("test term", "label")

        result = self.terms_repo.get_term(12345)

        self.assertEqual(result, ("test term", "label"))
        self.mock_cursor.execute.assert_called_once_with(
            "SELECT term, term_type FROM entity_terms WHERE hash = %s",
            (12345,),
        )

    def test_get_term_not_found(self) -> None:
        """Test getting a non-existent term"""
        self.mock_cursor.fetchone.return_value = None

        result = self.terms_repo.get_term(12345)

        self.assertIsNone(result)

    def test_batch_get_terms(self) -> None:
        """Test batch getting multiple terms"""
        self.mock_cursor.fetchall.return_value = [
            (12345, "term1", "label"),
            (67890, "term2", "alias"),
        ]

        result = self.terms_repo.batch_get_terms([12345, 67890, 99999])

        expected = TermsResponse(
            terms={
                12345: ("term1", "label"),
                67890: ("term2", "alias"),
            }
        )
        self.assertEqual(result, expected)
        self.mock_cursor.execute.assert_called_once()
        call_args = self.mock_cursor.execute.call_args
        self.assertIn("WHERE hash IN", call_args[0][0])
        self.assertEqual(call_args[0][1], [12345, 67890, 99999])

    def test_batch_get_terms_empty(self) -> None:
        """Test batch getting with empty list"""
        result = self.terms_repo.batch_get_terms([])

        self.assertEqual(result, TermsResponse(terms={}))

    def test_hash_exists_true(self) -> None:
        """Test checking if hash exists - found"""
        self.mock_cursor.fetchone.return_value = (1,)

        result = self.terms_repo.hash_exists(12345)

        self.assertTrue(result)
        self.mock_cursor.execute.assert_called_once_with(
            "SELECT 1 FROM entity_terms WHERE hash = %s LIMIT 1",
            (12345,),
        )

    def test_hash_exists_false(self) -> None:
        """Test checking if hash exists - not found"""
        self.mock_cursor.fetchone.return_value = None

        result = self.terms_repo.hash_exists(12345)

        self.assertFalse(result)
