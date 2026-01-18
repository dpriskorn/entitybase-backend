"""Unit tests for ThanksRepository."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timezone

from models.common import OperationResult
from models.thanks import ThankItem
from models.infrastructure.vitess.thanks_repository import ThanksRepository


class TestThanksRepository:
    @pytest.fixture
    def mock_connection_manager(self):
        return Mock()

    @pytest.fixture
    def mock_id_resolver(self):
        return Mock()

    @pytest.fixture
    def repository(self, mock_connection_manager, mock_id_resolver):
        return ThanksRepository(mock_connection_manager, mock_id_resolver)

    def test_send_thank_success(
        self, repository, mock_connection_manager, mock_id_resolver
    ):
        """Test successful thank sending."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchone.side_effect = [(456,)]  # to_user_id
        mock_cursor.fetchone.return_value = None  # no existing thank
        mock_cursor.lastrowid = 789

        result = repository.send_thank(123, "Q42", 100)

        assert result.success is True
        assert result.data == 789
        assert result.error is None

    def test_send_thank_invalid_parameters(self, repository):
        """Test send_thank with invalid parameters."""
        result = repository.send_thank(0, "Q42", 100)
        assert result.success is False
        assert "Invalid parameters" in result.error

    def test_send_thank_entity_not_found(
        self, repository, mock_connection_manager, mock_id_resolver
    ):
        """Test send_thank when entity not found."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_id_resolver.resolve_id.return_value = None

        result = repository.send_thank(123, "Q42", 100)

        assert result.success is False
        assert result.error == "Entity not found"

    def test_send_thank_revision_not_found(
        self, repository, mock_connection_manager, mock_id_resolver
    ):
        """Test send_thank when revision not found."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchone.return_value = None  # revision not found

        result = repository.send_thank(123, "Q42", 100)

        assert result.success is False
        assert result.error == "Revision not found"

    def test_send_thank_own_revision(
        self, repository, mock_connection_manager, mock_id_resolver
    ):
        """Test send_thank for own revision."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchone.side_effect = [(123,)]  # to_user_id == from_user_id

        result = repository.send_thank(123, "Q42", 100)

        assert result.success is False
        assert result.error == "Cannot thank your own revision"

    def test_send_thank_already_thanked(
        self, repository, mock_connection_manager, mock_id_resolver
    ):
        """Test send_thank when already thanked."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchone.side_effect = [(456,), (1,)]  # to_user_id, existing thank

        result = repository.send_thank(123, "Q42", 100)

        assert result.success is False
        assert result.error == "Already thanked this revision"

    def test_send_thank_database_error(
        self, repository, mock_connection_manager, mock_id_resolver
    ):
        """Test send_thank with database error."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchone.side_effect = Exception("Database error")

        result = repository.send_thank(123, "Q42", 100)

        assert result.success is False
        assert "Database error" in result.error

    def test_get_thanks_received_success(self, repository, mock_connection_manager):
        """Test successful get_thanks_received."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            (1, 123, 456, "Q42", 100, datetime(2023, 1, 1, tzinfo=timezone.utc))
        ]
        mock_cursor.fetchone.return_value = (1,)

        result = repository.get_thanks_received(456, 24, 50, 0)

        assert result.success is True
        data = result.data
        assert len(data["thanks"]) == 1
        assert data["total_count"] == 1
        assert data["has_more"] is False

    def test_get_thanks_received_pagination(self, repository, mock_connection_manager):
        """Test get_thanks_received with pagination."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        # Mock 55 thanks total, fetching 50 with offset 0, so has_more=True
        mock_cursor.fetchall.return_value = [
            (i, 123, 456, "Q42", 100, datetime(2023, 1, 1, tzinfo=timezone.utc))
            for i in range(1, 51)
        ]
        mock_cursor.fetchone.return_value = (55,)

        result = repository.get_thanks_received(456, 24, 50, 0)

        assert result.success is True
        data = result.data
        assert len(data["thanks"]) == 50
        assert data["total_count"] == 55
        assert data["has_more"] is True

    def test_get_thanks_received_empty(self, repository, mock_connection_manager):
        """Test get_thanks_received with no results."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchall.return_value = []
        mock_cursor.fetchone.return_value = (0,)

        result = repository.get_thanks_received(456, 24, 50, 0)

        assert result.success is True
        data = result.data
        assert len(data["thanks"]) == 0
        assert data["total_count"] == 0
        assert data["has_more"] is False

    def test_get_thanks_received_offset_pagination(self, repository, mock_connection_manager):
        """Test get_thanks_received with offset pagination."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        # Mock with offset 50, limit 10, total 55, so has_more = False
        mock_cursor.fetchall.return_value = [
            (i, 123, 456, "Q42", 100, datetime(2023, 1, 1, tzinfo=timezone.utc)) for i in range(51, 56)
        ]
        mock_cursor.fetchone.return_value = (55,)

        result = repository.get_thanks_received(456, 24, 10, 50)

        assert result.success is True
        data = result.data
        assert len(data["thanks"]) == 5
        assert data["total_count"] == 55
        assert data["has_more"] is False

    def test_get_thanks_received_invalid_params(self, repository):
        """Test get_thanks_received with invalid parameters."""
        result = repository.get_thanks_received(0, 24, 50, 0)
        assert result.success is False
        assert "Invalid parameters" in result.error

    def test_get_thanks_received_database_error(
        self, repository, mock_connection_manager
    ):
        """Test get_thanks_received with database error."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.execute.side_effect = Exception("Database error")

        result = repository.get_thanks_received(456, 24, 50, 0)

        assert result.success is False
        assert "Database error" in result.error

    def test_get_thanks_sent_success(self, repository, mock_connection_manager):
        """Test successful get_thanks_sent."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            (1, 123, 456, "Q42", 100, datetime(2023, 1, 1, tzinfo=timezone.utc))
        ]
        mock_cursor.fetchone.return_value = (1,)

        result = repository.get_thanks_sent(123, 24, 50, 0)

        assert result.success is True
        data = result.data
        assert len(data["thanks"]) == 1
        assert data["total_count"] == 1
        assert data["has_more"] is False

    def test_get_thanks_sent_pagination(self, repository, mock_connection_manager):
        """Test get_thanks_sent with pagination."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        # Mock 55 thanks total, fetching 50 with offset 0, so has_more=True
        mock_cursor.fetchall.return_value = [
            (i, 123, 456, "Q42", 100, datetime(2023, 1, 1, tzinfo=timezone.utc))
            for i in range(1, 51)
        ]
        mock_cursor.fetchone.return_value = (55,)

        result = repository.get_thanks_sent(123, 24, 50, 0)

        assert result.success is True
        data = result.data
        assert len(data["thanks"]) == 50
        assert data["total_count"] == 55
        assert data["has_more"] is True

    def test_get_thanks_sent_empty(self, repository, mock_connection_manager):
        """Test get_thanks_sent with no results."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchall.return_value = []
        mock_cursor.fetchone.return_value = (0,)

        result = repository.get_thanks_sent(123, 24, 50, 0)

        assert result.success is True
        data = result.data
        assert len(data["thanks"]) == 0
        assert data["total_count"] == 0
        assert data["has_more"] is False

    def test_get_thanks_sent_offset_pagination(self, repository, mock_connection_manager):
        """Test get_thanks_sent with offset pagination."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        # Mock with offset 50, limit 10, total 55, so has_more = False
        mock_cursor.fetchall.return_value = [
            (i, 123, 456, "Q42", 100, datetime(2023, 1, 1, tzinfo=timezone.utc)) for i in range(51, 56)
        ]
        mock_cursor.fetchone.return_value = (55,)

        result = repository.get_thanks_sent(123, 24, 10, 50)

        assert result.success is True
        data = result.data
        assert len(data["thanks"]) == 5
        assert data["total_count"] == 55
        assert data["has_more"] is False

    def test_get_thanks_sent_invalid_params(self, repository):
        """Test get_thanks_sent with invalid parameters."""
        result = repository.get_thanks_sent(0, 24, 50, 0)
        assert result.success is False
        assert "Invalid parameters" in result.error

    def test_get_revision_thanks_success(
        self, repository, mock_connection_manager, mock_id_resolver
    ):
        """Test successful get_revision_thanks."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchall.return_value = [
            (1, 123, 456, "Q42", 100, datetime(2023, 1, 1, tzinfo=timezone.utc))
        ]

        result = repository.get_revision_thanks("Q42", 100)

        assert result.success is True
        thanks = result.data
        assert len(thanks) == 1
        assert thanks[0].id == 1

    def test_get_revision_thanks_empty(
        self, repository, mock_connection_manager, mock_id_resolver
    ):
        """Test get_revision_thanks with no results."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchall.return_value = []

        result = repository.get_revision_thanks("Q42", 100)

        assert result.success is True
        thanks = result.data
        assert len(thanks) == 0

    def test_get_revision_thanks_multiple(self, repository, mock_connection_manager, mock_id_resolver):
        """Test get_revision_thanks with multiple thanks."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchall.return_value = [
            (1, 123, 456, "Q42", 100, datetime(2023, 1, 1, tzinfo=timezone.utc)),
            (2, 124, 456, "Q42", 100, datetime(2023, 1, 2, tzinfo=timezone.utc)),
            (3, 125, 456, "Q42", 100, datetime(2023, 1, 3, tzinfo=timezone.utc)),
        ]

        result = repository.get_revision_thanks("Q42", 100)

        assert result.success is True
        thanks = result.data
        assert len(thanks) == 3
        assert thanks[0].id == 1
        assert thanks[1].id == 2
        assert thanks[2].id == 3

    def test_get_revision_thanks_invalid_params(self, repository):
        """Test get_revision_thanks with invalid parameters."""
        result = repository.get_revision_thanks("", 100)
        assert result.success is False
        assert "Invalid parameters" in result.error

        result = repository.get_revision_thanks("Q42", 0)
        assert result.success is False
        assert "Invalid parameters" in result.error

    def test_get_revision_thanks_database_error(
        self, repository, mock_connection_manager, mock_id_resolver
    ):
        """Test get_revision_thanks with database error."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connection_manager.get_connection.return_value.__enter__.return_value = (
            mock_conn
        )
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.execute.side_effect = Exception("Database error")

        result = repository.get_revision_thanks("Q42", 100)

        assert result.success is False
        assert "Database error" in result.error
