from unittest.mock import Mock
from models.infrastructure.vitess.backlink_repository import BacklinkRepository


class TestBacklinkRepository:
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.connection_manager = Mock()
        self.repository = BacklinkRepository(self.connection_manager)
        self.conn = Mock()

    def test_insert_backlinks_empty_list(self) -> None:
        """Test inserting empty backlinks list does nothing."""
        backlinks: list[tuple[int, int, int, str, str]] = []
        self.repository.insert_backlinks(self.conn, backlinks)
        self.conn.cursor.assert_not_called()

    def test_insert_backlinks_single(self) -> None:
        """Test inserting a single backlink."""
        backlinks: list[tuple[int, int, int, str, str]] = [
            (123, 456, 789, "P31", "normal")
        ]

        cursor_mock = Mock()
        self.conn.cursor.return_value.__enter__.return_value = cursor_mock

        self.repository.insert_backlinks(self.conn, backlinks)

        cursor_mock.executemany.assert_called_once_with(
            """
            INSERT INTO entity_backlinks 
            (referenced_internal_id, referencing_internal_id, statement_hash, property_id, rank)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            referenced_internal_id = referenced_internal_id  -- no-op, just to handle duplicates
            """,
            backlinks,
        )

    def test_insert_backlinks_multiple(self) -> None:
        """Test inserting multiple backlinks."""
        backlinks: list[tuple[int, int, int, str, str]] = [
            (123, 456, 789, "P31", "normal"),
            (124, 457, 790, "P32", "preferred"),
        ]

        cursor_mock = Mock()
        self.conn.cursor.return_value.__enter__.return_value = cursor_mock

        self.repository.insert_backlinks(self.conn, backlinks)

        cursor_mock.executemany.assert_called_once_with(
            """
            INSERT INTO entity_backlinks 
            (referenced_internal_id, referencing_internal_id, statement_hash, property_id, rank)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            referenced_internal_id = referenced_internal_id  -- no-op, just to handle duplicates
            """,
            backlinks,
        )

    def test_delete_backlinks_for_entity(self) -> None:
        """Test deleting all backlinks for a referencing entity."""
        referencing_internal_id = 456

        cursor_mock = Mock()
        self.conn.cursor.return_value.__enter__.return_value = cursor_mock

        self.repository.delete_backlinks_for_entity(self.conn, referencing_internal_id)

        cursor_mock.execute.assert_called_once_with(
            "DELETE FROM entity_backlinks WHERE referencing_internal_id = %s",
            (referencing_internal_id,),
        )

    def test_get_backlinks_no_results(self) -> None:
        """Test getting backlinks when none exist."""
        referenced_internal_id = 123

        cursor_mock = Mock()
        cursor_mock.fetchall.return_value = []
        self.conn.cursor.return_value.__enter__.return_value = cursor_mock

        result = self.repository.get_backlinks(self.conn, referenced_internal_id)

        cursor_mock.execute.assert_called_once_with(
            """
            SELECT referencing_internal_id, statement_hash, property_id, rank
            FROM entity_backlinks
            WHERE referenced_internal_id = %s
            ORDER BY statement_hash
            LIMIT %s OFFSET %s
            """,
            (referenced_internal_id, 100, 0),
        )
        assert result == []

    def test_get_backlinks_with_results(self) -> None:
        """Test getting backlinks with results."""
        referenced_internal_id = 123

        cursor_mock = Mock()
        cursor_mock.fetchall.return_value = [
            (456, 789, "P31", "normal"),
            (457, 790, "P32", "preferred"),
        ]
        self.conn.cursor.return_value.__enter__.return_value = cursor_mock

        result = self.repository.get_backlinks(self.conn, referenced_internal_id)

        expected = [
            {
                "referencing_internal_id": 456,
                "statement_hash": 789,
                "property_id": "P31",
                "rank": "normal",
            },
            {
                "referencing_internal_id": 457,
                "statement_hash": 790,
                "property_id": "P32",
                "rank": "preferred",
            },
        ]
        assert result == expected

    def test_get_backlinks_with_pagination(self) -> None:
        """Test getting backlinks with custom limit and offset."""
        referenced_internal_id = 123
        limit = 50
        offset = 10

        cursor_mock = Mock()
        cursor_mock.fetchall.return_value = []
        self.conn.cursor.return_value.__enter__.return_value = cursor_mock

        result = self.repository.get_backlinks(
            self.conn, referenced_internal_id, limit, offset
        )

        cursor_mock.execute.assert_called_once_with(
            """
            SELECT referencing_internal_id, statement_hash, property_id, rank
            FROM entity_backlinks
            WHERE referenced_internal_id = %s
            ORDER BY statement_hash
            LIMIT %s OFFSET %s
            """,
            (referenced_internal_id, limit, offset),
        )
        assert result == []

    def test_connection_context_manager(self) -> None:
        """Test that cursor is properly used as context manager."""
        backlinks: list[tuple[int, int, int, str, str]] = [
            (123, 456, 789, "P31", "normal")
        ]

        cursor_mock = Mock()
        self.conn.cursor.return_value.__enter__.return_value = cursor_mock
        self.conn.cursor.return_value.__exit__.return_value = None

        self.repository.insert_backlinks(self.conn, backlinks)

        self.conn.cursor.assert_called_once()
        cursor_mock.__enter__.assert_called_once()
        cursor_mock.__exit__.assert_called_once()
