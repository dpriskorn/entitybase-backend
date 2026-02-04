"""Unit tests for read."""

from unittest.mock import MagicMock

import pytest

from models.rest_api.entitybase.v1.handlers.entity.read import EntityReadHandler


class TestEntityReadHandler:
    """Unit tests for EntityReadHandler."""

    def test_get_entity_not_found(self) -> None:
        """Test entity retrieval when entity doesn't exist."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = MagicMock()

        mock_vitess.entity_exists.return_value = False

        handler = EntityReadHandler(state=mock_state)

        with pytest.raises(Exception):  # Should raise validation error
            handler.get_entity("Q999")

        mock_vitess.entity_exists.assert_called_once_with("Q999")

    def test_get_entity_no_head_revision(self) -> None:
        """Test entity retrieval when no head revision exists."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = MagicMock()

        mock_vitess.entity_exists.return_value = True
        mock_vitess.get_head.return_value = 0  # No head revision

        handler = EntityReadHandler(state=mock_state)

        with pytest.raises(Exception):  # Should raise validation error
            handler.get_entity("Q42")

    def test_get_entity_vitess_not_initialized(self) -> None:
        """Test entity retrieval when Vitess client is not initialized."""
        mock_state = MagicMock()
        mock_state.vitess_client = None

        handler = EntityReadHandler(state=mock_state)

        with pytest.raises(Exception):  # Should raise validation error
            handler.get_entity("Q42")

    def test_get_entity_s3_not_initialized(self) -> None:
        """Test entity retrieval when S3 client is not initialized."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = None

        mock_vitess.entity_exists.return_value = True
        mock_vitess.get_head.return_value = 12345

        handler = EntityReadHandler(state=mock_state)

        with pytest.raises(Exception):  # Should raise validation error
            handler.get_entity("Q42")

    def test_get_entity_s3_read_failure(self) -> None:
        """Test entity retrieval when S3 read fails."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_s3 = MagicMock()
        mock_state.vitess_client = mock_vitess
        mock_state.s3_client = mock_s3

        mock_vitess.entity_exists.return_value = True
        mock_vitess.get_head.return_value = 12345
        mock_s3.read_revision.side_effect = Exception("S3 read failed")

        handler = EntityReadHandler(state=mock_state)

        with pytest.raises(Exception):  # Should raise validation error
            handler.get_entity("Q42")

    def test_get_entity_history_success(self) -> None:
        """Test successful entity history retrieval."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess

        mock_vitess.entity_exists.return_value = True
        mock_history = [
            {"revision_id": 12345, "timestamp": "2023-01-01", "user": "test_user"},
            {"revision_id": 12344, "timestamp": "2023-01-02", "user": "test_user2"},
        ]
        mock_vitess.get_entity_history.return_value = mock_history

        handler = EntityReadHandler(state=mock_state)
        result = handler.get_entity_history("Q42", limit=10, offset=0)

        assert result == mock_history
        mock_vitess.entity_exists.assert_called_once_with("Q42")
        mock_vitess.get_entity_history.assert_called_once_with("Q42", 10, 0)

    def test_get_entity_history_not_found(self) -> None:
        """Test entity history retrieval when entity doesn't exist."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess

        mock_vitess.entity_exists.return_value = False

        handler = EntityReadHandler(state=mock_state)

        with pytest.raises(Exception):  # Should raise validation error
            handler.get_entity_history("Q999")

    def test_get_entity_history_vitess_failure(self) -> None:
        """Test entity history retrieval when Vitess fails."""
        mock_state = MagicMock()
        mock_vitess = MagicMock()
        mock_state.vitess_client = mock_vitess

        mock_vitess.entity_exists.return_value = True
        mock_vitess.get_entity_history.side_effect = Exception("Vitess query failed")

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

    def test_get_entity_revision_s3_read_failure(self) -> None:
        """Test entity revision retrieval when S3 read fails."""
        mock_state = MagicMock()
        mock_s3 = MagicMock()
        mock_state.s3_client = mock_s3

        mock_s3.read_revision.side_effect = Exception("S3 read failed")

        handler = EntityReadHandler(state=mock_state)

        with pytest.raises(Exception):  # Should raise validation error
            handler.get_entity_revision("Q42", 12345)

    def test_get_entity_revision_not_found(self) -> None:
        """Test entity revision retrieval when revision doesn't exist."""
        mock_state = MagicMock()
        mock_s3 = MagicMock()
        mock_state.s3_client = mock_s3

        mock_s3.read_revision.side_effect = Exception("Revision not found")

        handler = EntityReadHandler(state=mock_state)

        with pytest.raises(Exception):  # Should raise validation error
            handler.get_entity_revision("Q42", 99999)

