"""Unit tests for ThanksRepository."""

import pytest
from unittest.mock import MagicMock

from models.infrastructure.vitess.repositories.thanks import ThanksRepository
from models.data.infrastructure.vitess.records.thanks import ThankItem


class TestThanksRepository:
    """Unit tests for ThanksRepository."""

    def test_send_thank_success(self):
        """Test successful thank sending."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchone.side_effect = [(456,), None]  # author, no existing thank
        mock_cursor.lastrowid = 789
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = ThanksRepository(vitess_client=mock_vitess_client)

        result = repo.send_thank(111, "Q1", 1)

        assert result.success is True
        assert result.data == 789

    def test_send_thank_entity_not_found(self):
        """Test sending thank when entity not found."""
        mock_vitess_client = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = None
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = ThanksRepository(vitess_client=mock_vitess_client)

        result = repo.send_thank(111, "Q999", 1)

        assert result.success is False
        assert "Entity not found" in result.error

    def test_send_thank_revision_not_found(self):
        """Test sending thank when revision not found."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchone.return_value = None  # no revision
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = ThanksRepository(vitess_client=mock_vitess_client)

        result = repo.send_thank(111, "Q1", 1)

        assert result.success is False
        assert "Revision not found" in result.error

    def test_send_thank_own_revision(self):
        """Test sending thank to own revision."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchone.return_value = (111,)  # same user
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = ThanksRepository(vitess_client=mock_vitess_client)

        result = repo.send_thank(111, "Q1", 1)

        assert result.success is False
        assert "Cannot thank your own revision" in result.error

    def test_send_thank_already_thanked(self):
        """Test sending thank when already thanked."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchone.side_effect = [(456,), (1,)]  # author, existing thank
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = ThanksRepository(vitess_client=mock_vitess_client)

        result = repo.send_thank(111, "Q1", 1)

        assert result.success is False
        assert "Already thanked" in result.error

    def test_send_thank_invalid_params(self):
        """Test sending thank with invalid parameters."""
        mock_vitess_client = MagicMock()

        repo = ThanksRepository(vitess_client=mock_vitess_client)

        result = repo.send_thank(0, "Q1", 1)

        assert result.success is False
        assert "Invalid parameters" in result.error

    def test_get_thanks_received_success(self):
        """Test getting thanks received."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [(1, 111, 222, "Q1", 1, "2023-01-01")],  # thanks
            (1,)  # total count
        ]
        mock_vitess_client.cursor = mock_cursor

        repo = ThanksRepository(vitess_client=mock_vitess_client)

        result = repo.get_thanks_received(222)

        assert result.success is True
        assert len(result.data["thanks"]) == 1
        assert isinstance(result.data["thanks"][0], ThankItem)

    def test_get_thanks_received_invalid_params(self):
        """Test getting thanks received with invalid params."""
        mock_vitess_client = MagicMock()

        repo = ThanksRepository(vitess_client=mock_vitess_client)

        result = repo.get_thanks_received(0)

        assert result.success is False
        assert "Invalid parameters" in result.error

    def test_get_revision_thanks_success(self):
        """Test getting thanks for a revision."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchall.return_value = [(1, 111, 222, "Q1", 1, "2023-01-01")]
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = ThanksRepository(vitess_client=mock_vitess_client)

        result = repo.get_revision_thanks("Q1", 1)

        assert result.success is True
        assert len(result.data) == 1
        assert isinstance(result.data[0], ThankItem)

    def test_send_thank_already_sent(self):
        """Test sending thank when already sent."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_id_resolver = MagicMock()
        mock_id_resolver.resolve_id.return_value = 123
        mock_cursor.fetchone.side_effect = [(456,), (1,)]  # author, existing thank
        mock_vitess_client.cursor = mock_cursor
        mock_vitess_client.id_resolver = mock_id_resolver

        repo = ThanksRepository(vitess_client=mock_vitess_client)

        result = repo.send_thank(111, "Q1", 1)

        assert result.success is False
        assert "Already thanked" in result.error

    def test_send_thank_database_error(self):
        """Test sending thank with database error."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("DB error")
        mock_vitess_client.cursor = mock_cursor

        repo = ThanksRepository(vitess_client=mock_vitess_client)

        result = repo.send_thank(111, "Q1", 1)

        assert result.success is False
        assert "DB error" in result.error

    def test_get_thanks_received_pagination(self):
        """Test getting thanks received with pagination."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [(1, 111, 222, "Q1", 1, "2023-01-01"), (2, 112, 222, "Q2", 2, "2023-01-02")],  # thanks
            (5,)  # total count
        ]
        mock_vitess_client.cursor = mock_cursor

        repo = ThanksRepository(vitess_client=mock_vitess_client)

        result = repo.get_thanks_received(222, limit=2, offset=1)

        assert result.success is True
        assert len(result.data["thanks"]) == 2
        assert result.data["total_count"] == 5
        assert result.data["has_more"] is True

    def test_get_thanks_received_include_removed(self):
        """Test getting thanks received including removed ones."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [(1, 111, 222, "Q1", 1, "2023-01-01")],  # thanks
            (1,)  # total count
        ]
        mock_vitess_client.cursor = mock_cursor

        repo = ThanksRepository(vitess_client=mock_vitess_client)

        result = repo.get_thanks_received(222, include_removed=True)

        assert result.success is True
        assert len(result.data["thanks"]) == 1

    def test_get_thanks_sent_success(self):
        """Test getting thanks sent."""
        mock_vitess_client = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = [
            [(1, 111, 222, "Q1", 1, "2023-01-01")],  # thanks
            (1,)  # total count
        ]
        mock_vitess_client.cursor = mock_cursor

        repo = ThanksRepository(vitess_client=mock_vitess_client)

        result = repo.get_thanks_sent(111)

        assert result.success is True
        assert len(result.data["thanks"]) == 1
        assert result.data["total_count"] == 1

    def test_get_thanks_sent_invalid_params(self):
        """Test getting thanks sent with invalid params."""
        mock_vitess_client = MagicMock()

        repo = ThanksRepository(vitess_client=mock_vitess_client)

        result = repo.get_thanks_sent(0)

        assert result.success is False
        assert "Invalid parameters" in result.error
