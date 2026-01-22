from unittest.mock import Mock
from models.infrastructure.vitess.repositories.metadata import MetadataRepository
from models.infrastructure.vitess.client import VitessClient


class TestMetadataRepository:
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.connection_manager = Mock()
        self.vitess_client = Mock(spec=VitessClient)
        self.repository = MetadataRepository(vitess_client=self.vitess_client)

    def test_insert_metadata_content_new(self) -> None:
        """Test inserting new metadata content."""
        conn = Mock()
        cursor = Mock()
        conn.cursor = Mock(return_value=cursor)
        cursor.__exit__ = Mock(return_value=None)

        self.repository.insert_metadata_content(12345, "labels")

        cursor.execute.assert_called_with(
            """
            INSERT INTO metadata_content (content_hash, content_type, ref_count)
            VALUES (%s, %s, 1)
            ON DUPLICATE KEY UPDATE ref_count = ref_count + 1
            """,
            (12345, "labels"),
        )

    def test_get_metadata_content_exists(self) -> None:
        """Test getting existing metadata content."""
        conn = Mock()
        cursor = Mock()
        conn.cursor = Mock(return_value=cursor)
        cursor.__exit__ = Mock(return_value=None)
        cursor.fetchone.return_value = (5,)  # ref_count = 5

        result = self.repository.get_metadata_content(12345, "labels")

        cursor.execute.assert_called_with(
            "SELECT ref_count FROM metadata_content WHERE content_hash = %s AND content_type = %s",
            (12345, "labels"),
        )
        assert result == {"ref_count": 5}

    def test_get_metadata_content_not_exists(self) -> None:
        """Test getting non-existent metadata content."""
        conn = Mock()
        cursor = Mock()
        conn.cursor = Mock(return_value=cursor)
        cursor.__exit__ = Mock(return_value=None)
        cursor.fetchone.return_value = None

        result = self.repository.get_metadata_content(12345, "labels")

        assert result is None

    def test_decrement_ref_count_above_zero(self) -> None:
        """Test decrementing ref_count when it remains above 0."""
        conn = Mock()
        cursor = Mock()
        conn.cursor = Mock(return_value=cursor)
        cursor.__exit__ = Mock(return_value=None)
        cursor.fetchone.return_value = (3,)  # ref_count = 3 after decrement

        result = self.repository.decrement_ref_count(12345, "labels")

        cursor.execute.assert_any_call(
            """
            UPDATE metadata_content
            SET ref_count = ref_count - 1
            WHERE content_hash = %s AND content_type = %s
            """,
            (12345, "labels"),
        )
        cursor.execute.assert_any_call(
            "SELECT ref_count FROM metadata_content WHERE content_hash = %s AND content_type = %s",
            (12345, "labels"),
        )
        assert result is False

    def test_decrement_ref_count_reaches_zero(self) -> None:
        """Test decrementing ref_count when it reaches 0."""
        conn = Mock()
        cursor = Mock()
        conn.cursor = Mock(return_value=cursor)
        cursor.__exit__ = Mock(return_value=None)
        cursor.fetchone.return_value = (0,)  # ref_count = 0 after decrement

        result = self.repository.decrement_ref_count(12345, "labels")

        assert result is True

    def test_delete_metadata_content(self) -> None:
        """Test deleting metadata content."""
        conn = Mock()
        cursor = Mock()
        conn.cursor = Mock(return_value=cursor)
        cursor.__exit__ = Mock(return_value=None)

        self.repository.delete_metadata_content(12345, "labels")

        cursor.execute.assert_called_with(
            "DELETE FROM metadata_content WHERE content_hash = %s AND content_type = %s AND ref_count <= 0",
            (12345, "labels"),
        )

    def test_connection_context_management(self) -> None:
        """Test that database connections are properly managed."""
        conn = Mock()
        cursor = Mock()
        conn.cursor = Mock(return_value=cursor)
        cursor.__exit__ = Mock(return_value=None)
        conn.cursor.return_value.__exit__.return_value = None

        self.repository.insert_metadata_content(12345, "labels")

        conn.cursor.assert_called_once()

        conn.cursor.return_value.__exit__.assert_called_once()
