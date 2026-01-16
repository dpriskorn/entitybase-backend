import pytest
from unittest.mock import Mock
from models.infrastructure.vitess.backlink_repository import BacklinkRepository, BacklinkEntry


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
        self.conn.cursor = Mock(return_value=cursor_mock)

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
        self.conn.cursor = Mock(return_value=cursor_mock)

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
        self.conn.cursor = Mock(return_value=cursor_mock)

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
        self.conn.cursor = Mock(return_value=cursor_mock)

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
        self.conn.cursor = Mock(return_value=cursor_mock)

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
        self.conn.cursor = Mock(return_value=cursor_mock)

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
        self.conn.cursor = Mock(return_value=cursor_mock)
        cursor_mock.__exit__ = Mock(return_value=None)

        self.repository.insert_backlinks(self.conn, backlinks)

        self.conn.cursor.assert_called_once()
        cursor_mock.__enter__.assert_called_once()
        cursor_mock.__exit__.assert_called_once()

    def test_insert_backlink_statistics_success(self) -> None:
        """Test successful insertion of backlink statistics."""
        date = "2024-01-13"
        total_backlinks = 1000
        unique_entities = 500
        top_entities = [{"id": "Q42", "count": 50}, {"id": "Q43", "count": 45}]

        cursor_mock = Mock()
        self.conn.cursor = Mock(return_value=cursor_mock)

        self.repository.insert_backlink_statistics(
            self.conn, date, total_backlinks, unique_entities, top_entities
        )

        cursor_mock.execute.assert_called_once()
        args, kwargs = cursor_mock.execute.call_args

        # Check the SQL query
        expected_query = """
            INSERT INTO backlink_statistics
            (date, total_backlinks, unique_entities_with_backlinks, top_entities_by_backlinks)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            total_backlinks = VALUES(total_backlinks),
            unique_entities_with_backlinks = VALUES(unique_entities_with_backlinks),
            top_entities_by_backlinks = VALUES(top_entities_by_backlinks)
            """
        assert args[0].strip() == expected_query.strip()

        # Check the parameters
        params = args[1]
        assert params[0] == date
        assert params[1] == total_backlinks
        assert params[2] == unique_entities
        # JSON should be serialized
        import json

        assert params[3] == json.dumps(top_entities)

    def test_insert_backlink_statistics_invalid_date(self) -> None:
        """Test validation of invalid date format."""
        from models.validation.utils import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            self.repository.insert_backlink_statistics(
                self.conn, "invalid-date", 100, 50, []
            )

        assert "Invalid date format" in str(exc_info.value)

    def test_insert_backlink_statistics_negative_counts(self) -> None:
        """Test validation of negative count values."""
        from models.validation.utils import ValidationError

        # Test negative total_backlinks
        with pytest.raises(ValidationError) as exc_info:
            self.repository.insert_backlink_statistics(
                self.conn, "2024-01-13", -1, 50, []
            )
        assert "total_backlinks must be non-negative" in str(exc_info.value)

        # Test negative unique_entities
        with pytest.raises(ValidationError) as exc_info:
            self.repository.insert_backlink_statistics(
                self.conn, "2024-01-13", 100, -1, []
            )
        assert "unique_entities_with_backlinks must be non-negative" in str(
            exc_info.value
        )

    def test_insert_backlink_statistics_invalid_top_entities(self) -> None:
        """Test validation of invalid top_entities type."""
        from models.validation.utils import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            self.repository.insert_backlink_statistics(
                self.conn, "2024-01-13", 100, 50, "not-a-list"
            )

        assert "top_entities_by_backlinks must be a list" in str(exc_info.value)

    def test_insert_backlink_statistics_json_serialization_error(self) -> None:
        """Test handling of JSON serialization errors."""
        from models.validation.utils import ValidationError

        # Create an object that can't be JSON serialized
        class NonSerializable:
            pass

        top_entities = [{"valid": "data"}, NonSerializable()]

        with pytest.raises(ValidationError) as exc_info:
            self.repository.insert_backlink_statistics(
                self.conn, "2024-01-13", 100, 50, top_entities
            )

        assert "Failed to serialize top_entities_by_backlinks" in str(exc_info.value)

    def test_insert_backlink_statistics_database_error(self) -> None:
        """Test handling of database execution errors."""
        cursor_mock = Mock()
        cursor_mock.execute.side_effect = Exception("Database connection failed")
        self.conn.cursor = Mock(return_value=cursor_mock)

        with pytest.raises(Exception) as exc_info:
            self.repository.insert_backlink_statistics(
                self.conn, "2024-01-13", 100, 50, []
            )

        assert "Database connection failed" in str(exc_info.value)
