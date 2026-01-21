from unittest.mock import Mock

from models.infrastructure.vitess.repositories.head import HeadRepository


class TestHeadRepository:
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.connection_manager = Mock()
        self.id_resolver = Mock()
        self.repository = HeadRepository(self.id_resolver)

    def test_get_head_revision_exists(self) -> None:
        """Test getting head revision when entity exists."""
        conn = Mock()
        cursor = Mock()
        conn.cursor = Mock(return_value=cursor)
        cursor.__exit__ = Mock(return_value=None)
        conn.__exit__ = Mock(return_value=None)
        self.connection_manager.get_connection = Mock(return_value=conn)

        cursor.fetchone.return_value = (123,)

        result = self.repository.get_head_revision(42)

        assert result == 123
        cursor.execute.assert_called_once_with(
            """SELECT head_revision_id FROM entity_head WHERE internal_id = %s""",
            (42,),
        )

    def test_get_head_revision_not_exists(self) -> None:
        """Test getting head revision when entity does not exist."""
        conn = Mock()
        cursor = Mock()
        conn.cursor = Mock(return_value=cursor)
        cursor.__exit__ = Mock(return_value=None)
        conn.__exit__ = Mock(return_value=None)
        self.connection_manager.get_connection = Mock(return_value=conn)

        cursor.fetchone.return_value = None

        result = self.repository.get_head_revision(42)

        assert result == 0
        cursor.execute.assert_called_once_with(
            """SELECT head_revision_id FROM entity_head WHERE internal_id = %s""",
            (42,),
        )
