"""Unit tests for read."""

from unittest.mock import MagicMock, patch

import pytest

from models.rest_api.entitybase.v1.handlers.entity.read import EntityReadHandler
from models.infrastructure.s3.exceptions import S3NotFoundError


class TestEntityReadHandler:
    """Unit tests for EntityReadHandler."""

    def test_get_entity_not_found(self) -> None:
        """Test entity retrieval when entity doesn't exist."""
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_state.s3_client = MagicMock()

        mock_mysql.entity_exists.return_value = False

        handler = EntityReadHandler(state=mock_state)

        with pytest.raises(Exception):  # Should raise validation error
            handler.get_entity("Q999")

        mock_mysql.entity_exists.assert_called_once_with("Q999")

    def test_get_entity_no_head_revision(self) -> None:
        """Test entity retrieval when no head revision exists."""
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_state.s3_client = MagicMock()

        mock_mysql.entity_exists.return_value = True
        mock_mysql.get_head.return_value = 0  # No head revision

        handler = EntityReadHandler(state=mock_state)

        with pytest.raises(Exception):  # Should raise validation error
            handler.get_entity("Q42")

    def test_get_entity_mysql_not_initialized(self) -> None:
        """Test entity retrieval when Sql client is not initialized."""
        mock_state = MagicMock()
        mock_state.mysql_client = None

        handler = EntityReadHandler(state=mock_state)

        with pytest.raises(Exception):  # Should raise validation error
            handler.get_entity("Q42")

    def test_get_entity_s3_not_initialized(self) -> None:
        """Test entity retrieval when S3 client is not initialized."""
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_state.s3_client = None

        mock_mysql.entity_exists.return_value = True
        mock_mysql.get_head.return_value = 12345

        handler = EntityReadHandler(state=mock_state)

        with pytest.raises(Exception):  # Should raise validation error
            handler.get_entity("Q42")

    def test_get_entity_s3_not_found(self) -> None:
        """Test entity retrieval when S3 object not found (404)."""
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_s3 = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_state.s3_client = mock_s3

        mock_mysql.entity_exists.return_value = True
        mock_mysql.get_head.return_value = 12345
        mock_s3.read_revision.side_effect = S3NotFoundError("Object not found: 12345")

        handler = EntityReadHandler(state=mock_state)

        with pytest.raises(Exception):  # Should raise validation error with 404
            handler.get_entity("Q42")

    def test_get_entity_s3_read_failure(self) -> None:
        """Test entity retrieval when S3 read fails (500)."""
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_s3 = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_state.s3_client = mock_s3

        mock_mysql.entity_exists.return_value = True
        mock_mysql.get_head.return_value = 12345
        mock_s3.read_revision.side_effect = Exception("S3 read failed")

        handler = EntityReadHandler(state=mock_state)

        with pytest.raises(Exception):  # Should raise validation error with 500
            handler.get_entity("Q42")

    def test_get_entity_history_success(self) -> None:
        """Test successful entity history retrieval."""
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_state.mysql_client = mock_mysql

        mock_mysql.entity_exists.return_value = True
        mock_history = [
            {"revision_id": 12345, "timestamp": "2023-01-01", "user": "test_user"},
            {"revision_id": 12344, "timestamp": "2023-01-02", "user": "test_user2"},
        ]
        mock_mysql.get_entity_history.return_value = mock_history

        handler = EntityReadHandler(state=mock_state)
        result = handler.get_entity_history("Q42", limit=10, offset=0)

        assert result == mock_history
        mock_mysql.entity_exists.assert_called_once_with("Q42")
        mock_mysql.get_entity_history.assert_called_once_with("Q42", 10, 0)

    def test_get_entity_history_not_found(self) -> None:
        """Test entity history retrieval when entity doesn't exist."""
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_state.mysql_client = mock_mysql

        mock_mysql.entity_exists.return_value = False

        handler = EntityReadHandler(state=mock_state)

        with pytest.raises(Exception):  # Should raise validation error
            handler.get_entity_history("Q999")

    def test_get_entity_history_mysql_failure(self) -> None:
        """Test entity history retrieval when Sql fails."""
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_state.mysql_client = mock_mysql

        mock_mysql.entity_exists.return_value = True
        mock_mysql.get_entity_history.side_effect = Exception("Sql query failed")

        handler = EntityReadHandler(state=mock_state)

        with pytest.raises(Exception):  # Should raise validation error
            handler.get_entity_history("Q42")

    def test_get_entity_revision_s3_not_initialized(self) -> None:
        """Test entity revision retrieval when S3 client is not initialized."""
        mock_state = MagicMock()
        mock_state.s3_client = None

        handler = EntityReadHandler(state=mock_state)

        with pytest.raises(Exception):  # Should raise validation error
            handler.get_entity_revision("Q42", 12345)

    def test_get_entity_revision_s3_not_found(self) -> None:
        """Test entity revision retrieval when S3 object not found (404)."""
        mock_state = MagicMock()
        mock_s3 = MagicMock()
        mock_state.s3_client = mock_s3

        mock_s3.read_revision.side_effect = S3NotFoundError("Revision not found")

        handler = EntityReadHandler(state=mock_state)

        with pytest.raises(Exception):  # Should raise validation error with 404
            handler.get_entity_revision("Q42", 99999)

    def test_get_entity_revision_s3_read_failure(self) -> None:
        """Test entity revision retrieval when S3 read fails (500)."""
        mock_state = MagicMock()
        mock_s3 = MagicMock()
        mock_state.s3_client = mock_s3

        mock_s3.read_revision.side_effect = Exception("S3 read failed")

        handler = EntityReadHandler(state=mock_state)

        with pytest.raises(Exception):  # Should raise validation error with 500
            handler.get_entity_revision("Q42", 12345)

    def test_get_entity_success(self) -> None:
        """Test successful entity retrieval (happy path)."""
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_s3 = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_state.s3_client = mock_s3

        mock_mysql.entity_exists.return_value = True
        mock_mysql.get_head.return_value = 42

        from models.data.infrastructure.s3.revision_data import S3RevisionData

        s3_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={
                "id": "Q42",
                "type": "item",
                "labels": {"en": {"language": "en", "value": "Test"}},
                "state": {
                    "is_semi_protected": False,
                    "is_locked": False,
                    "is_archived": False,
                    "is_dangling": True,
                    "is_mass_edit_protected": False,
                    "is_deleted": False,
                },
            },
            hash=123456789,
            created_at="2023-01-01T12:00:00Z",
        )
        mock_s3.read_revision.return_value = s3_revision_data

        handler = EntityReadHandler(state=mock_state)
        response = handler.get_entity("Q42")

        assert response.id == "Q42"
        assert response.revision_id == 42
        assert response.state.is_dangling is True
        assert response.state.is_deleted is not True
        mock_mysql.entity_exists.assert_called_once_with("Q42")
        mock_mysql.get_head.assert_called_once_with("Q42")

    def test_get_entity_deleted_state(self) -> None:
        """Test entity retrieval when entity is marked as deleted in state."""
        mock_state = MagicMock()
        mock_mysql = MagicMock()
        mock_s3 = MagicMock()
        mock_state.mysql_client = mock_mysql
        mock_state.s3_client = mock_s3

        mock_mysql.entity_exists.return_value = True
        mock_mysql.get_head.return_value = 42

        from models.data.infrastructure.s3.revision_data import S3RevisionData

        s3_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={
                "id": "Q42",
                "type": "item",
                "state": {
                    "is_deleted": True,
                    "is_semi_protected": False,
                    "is_locked": False,
                },
            },
            hash=123456789,
            created_at="2023-01-01T12:00:00Z",
        )
        mock_s3.read_revision.return_value = s3_revision_data

        handler = EntityReadHandler(state=mock_state)

        with pytest.raises(Exception):
            handler.get_entity("Q42")

    def test_get_entity_revision_success(self) -> None:
        """Test successful entity revision retrieval (happy path)."""
        mock_state = MagicMock()
        mock_s3 = MagicMock()
        mock_state.s3_client = mock_s3

        from models.data.infrastructure.s3.revision_data import S3RevisionData

        s3_revision_data = S3RevisionData(
            schema="1.0.0",
            revision={
                "id": "Q42",
                "type": "item",
                "labels": {"en": {"language": "en", "value": "Old Label"}},
            },
            hash=999,
            created_at="2023-01-01T12:00:00Z",
        )
        mock_s3.read_revision.return_value = s3_revision_data

        handler = EntityReadHandler(state=mock_state)
        response = handler.get_entity_revision("Q42", 1)

        assert response.id == "Q42"
        assert response.revision_id == 1
        mock_s3.read_revision.assert_called_once_with("Q42", 1)

    def test_get_entity_history_mysql_not_initialized(self) -> None:
        """Test entity history retrieval when Sql client is not initialized."""
        mock_state = MagicMock()
        mock_state.mysql_client = None

        handler = EntityReadHandler(state=mock_state)

        with pytest.raises(Exception):
            handler.get_entity_history("Q42")
